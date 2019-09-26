import logging
import time
from typing import List, Dict, Optional

from django.db import connections
from django.db.migrations.migration import Migration
from django.db.backends.dummy.base import (
    DatabaseWrapper as DummyDatabaseWrapper
)
from django.db.migrations.graph import Node
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.executor import MigrationExecutor
from django.db.backends.base.base import BaseDatabaseWrapper as DatabaseWrapper

logger = logging.getLogger(__name__)


class NavigatorError(Exception):
    pass


class Navigator:
    """Database migration helper class.

    Allows for migrations to be performed programmatically. Django
    documentation outlines how to perform the migrations manually on the
    host machine, but that doesn't bode well in automated deployment
    environments. Two separate commands, one to migrate and one to start
    the server, must be performed in order instead of running one command
    with the migration setup integrated into the startup logic. The migrate
    command also outputs a different unconfigurable logging format that isn't
    picked up very well in a centralized logging environment.

    Most of this code is pulled from the core django management commands
    and altered to fit the workflow from the core CLI command. For future
    reference, check `django.core.management.commands.migrate` and
    `django.core.management.commands`.

    Attributes:
        start: Start time of the previous migration action.
        _connections: Dictionary of current database connections indexed
            by their identifier in the settings.
    """
    def __init__(self):
        self.start: Optional[float] = None
        self._connections: Dict[str, DatabaseWrapper] = {}

        for key in connections.databases.keys():
            self._connections[key] = connections[key]

    @property
    def connections(self):
        if self._connections:
            return self._connections

        for key in connections.databases.keys():
            self._connections[key] = connections[key]

        return self._connections

    def close(self):
        if self._connections:
            for connection in self._connections.values():
                connection.close()
            self._connections = {}

    def log_migration_progress(
        self, action: str, migration: Optional[Migration] = None,
        fake: bool = False,
    ):
        """Logs migration progress for each migration.

        Args:
            action: String identifier of the migration action.
            migration: Migration being performed.
            fake: If the migration is being faked.
        """
        if action == 'apply_start':
            self.start = time.monotonic()
            logger.info("Migrating %s START", migration)
        elif action == 'apply_success':
            elapsed = '(%.3fs)' % (time.monotonic() - self.start)
            result = 'FAKED' if fake else 'SUCCESS'
            logger.info("Migrating %s %s %s", migration, result, elapsed)
        elif action == 'unapply_start':
            self.start = time.monotonic()
            logger.info("Reverting %s START", migration)
        elif action == 'unapply_success':
            elapsed = '(%.3fs)' % (time.monotonic() - self.start)
            result = 'FAKED' if fake else 'SUCCESS'
            logger.info("Revert %s %s %s", migration, result, elapsed)
        elif action == 'render_start':
            self.start = time.monotonic()
            logger.info('Rendering model states')
        elif action == 'render_success':
            elapsed = '(%.3fs)' % (time.monotonic() - self.start)
            logger.info('Rendering model states SUCCESS %s', elapsed)

    def get_unapplied_migrations(self) -> Dict[str, List[Node]]:
        """Returns a collection of migrations that have not been applied.

        Returns:
            Dictionary of migrations that need to be applied sorted by their
            application order and indexed by the database they need to be
            applied to.
        """
        migration_plans = {}

        # Collection migration plan for each database connection.
        for name, connection in self._connections.items():
            # Ignore any dummy database wrappers.
            if isinstance(connection, DummyDatabaseWrapper):
                continue

            loader = MigrationLoader(connection)
            graph = loader.graph
            leaf_nodes = graph.leaf_nodes()
            migration_plan = []
            visited_nodes = set()

            for leaf_node in leaf_nodes:
                for migration in graph.forwards_plan(leaf_node):
                    if migration in visited_nodes:
                        continue
                    node = graph.node_map[migration]
                    if node not in loader.applied_migrations:
                        migration_plan.append(node)
                    visited_nodes.add(migration)

            # Only add if there are unapplied migrations.
            if migration_plan:
                migration_plans[name] = migration_plan

        return migration_plans

    def migrate(self, fake: bool = False):
        """Migrates every database to the most recent version.

        Args:
            fake: If the migration should be rolled back after
                application.
        """
        if not self.get_unapplied_migrations():
            return

        for name, connection in self._connections.items():
            logger.info("Migrating database '%s'", name)
            # Hook for backends needing any database preparation.
            connection.prepare_database()
            # Find which apps have migrations and which do not.
            executor = MigrationExecutor(
                connection, self.log_migration_progress,
            )
            # Raise an error if any migrations are applied before
            # their dependencies.
            executor.loader.check_consistent_history(connection)

            # Before anything else, see if there's conflicting apps and drop
            # out hard if there are any
            conflicts = executor.loader.detect_conflicts()
            if conflicts:
                name_str = "; ".join(
                    "%s in %s" % (", ".join(names), app)
                    for app, names in conflicts.items()
                )
                raise NavigatorError(
                    "Conflicting migrations detected; multiple leaf nodes in "
                    "the migration graph: (%s).\nTo fix them merge "
                    "the database migrations." % name_str
                )

            targets = executor.loader.graph.leaf_nodes()
            executor.migrate(targets, fake=fake)
            logger.info("Database '%s' migration successful", name)

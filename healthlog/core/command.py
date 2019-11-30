import os
import logging

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '-h', '--host', default='localhost',
    help='Hostname to bind to.', envvar='HEALTH_LOG_SERVER_HOST',
)
@click.option(
    '-p', '--port', default=80,
    help='Port to bind to.', envvar='HEALTH_LOG_SERVER_PORT',
)
def main(**options):
    """Base command for the CLI.

    Args:
        **options: Arguments passed in from the CLI call.
    """
    from waitress import serve
    from django import setup
    from django.core.handlers.wsgi import WSGIHandler

    from healthlog.core.navigator import Navigator
    from healthlog.core.collector import Collector

    # Setup the django application registry
    os.environ['DJANGO_SETTINGS_MODULE'] = 'healthlog.core.settings'
    setup(set_prefix=False)

    from django.conf import settings

    # Check for any migrations to apply.
    navigator = Navigator()
    navigator.migrate()
    navigator.close()

    collector = Collector()
    collector.handle()
    logger.info('This is new')

    if settings.DEFAULT_ADMIN_EMAIL and settings.DEFAULT_ADMIN_PASSWORD:
        from healthlog.core.models import User
        logger.info('Creating default admin %s', settings.DEFAULT_ADMIN_EMAIL)
        user, created = User.objects.get_or_create(
            email=settings.DEFAULT_ADMIN_EMAIL
        )
        user.set_password(settings.DEFAULT_ADMIN_PASSWORD)
        user.is_admin = True
        user.save()
        logger.info('Default admin %s set', settings.DEFAULT_ADMIN_EMAIL)

    host = options.get('host')
    port = options.get('port')
    logger.info('Starting server at http://%s:%d', host, port)
    serve(WSGIHandler(), host=host, port=port, _quiet=True)



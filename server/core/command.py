import os
import logging

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '-h', '--host', default='localhost',
    help='Hostname to bind to.',
)
@click.option(
    '-p', '--port', default=80,
    help='Port to bind to.',
)
def main(**options):
    from waitress import serve
    from django import setup
    from django.core.handlers.wsgi import WSGIHandler

    from server.core.navigator import Navigator

    # Setup the django application registry
    os.environ['DJANGO_SETTINGS_MODULE'] = 'server.core.settings'
    setup(set_prefix=False)

    # Check for any migrations to apply.
    navigator = Navigator()
    navigator.migrate()
    navigator.close()

    host = options.get('host')
    port = options.get('port')
    logger.info('Starting server at http://%s:%d', host, port)
    serve(WSGIHandler(), host=host, port=port, _quiet=True)



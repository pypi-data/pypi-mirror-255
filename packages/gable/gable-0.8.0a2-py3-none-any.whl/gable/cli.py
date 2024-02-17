import shutil

import click
from gable.client import GableClient
from gable.helpers.jsonpickle import register_jsonpickle_handlers
from gable.helpers.logging import configure_default_click_logging
from gable.options import Context, endpoint_options, global_options
from loguru import logger

from .commands.auth import auth
from .commands.contract import contract
from .commands.data_asset import data_asset
from .commands.debug import debug
from .commands.ping import ping

# Configure default logging which uses click.echo(), this will be replaced if the --debug flag is passed
# to the CLI
configure_default_click_logging()
# Configure jsonpickle's custom serialization handlers
register_jsonpickle_handlers()


# Click normally wraps text at 80 characters, but this is too narrow and makes the help text difficult to read.
# This sets the max width to the width of the terminal, which is a better default.
@click.group(
    add_help_option=False,
    context_settings={"max_content_width": shutil.get_terminal_size().columns},
)
@global_options()
@click.version_option()
@click.pass_context
def cli(ctx):
    if ctx.obj is None:
        ctx.obj = Context()
    if ctx.obj.client is None:
        # Create a client without an endpoint or api key by default, this will either be overwritten when the
        # endpoint/api options are processed, or the client validation will fail when the client is used
        ctx.obj.client = GableClient("", "")


cli.add_command(auth)
cli.add_command(debug)
cli.add_command(contract)
cli.add_command(data_asset)
cli.add_command(ping)


if __name__ == "__main__":
    cli()

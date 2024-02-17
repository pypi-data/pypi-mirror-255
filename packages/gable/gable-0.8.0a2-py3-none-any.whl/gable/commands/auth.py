import click
from click.core import Context as ClickContext
from gable.options import global_options
from loguru import logger


@click.group()
def auth():
    """View configured Gable authentication information"""


@auth.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
)
@global_options()
@click.pass_context
def key(ctx: ClickContext):
    """Print the API Key gable is currently configured to use"""
    api_key = ctx.obj.client.api_key
    if api_key:
        logger.info("API Key in use: " + api_key)
        logger.info("To see your account's API Keys, visit your /settings page.")
    else:
        logger.info("No API Key configured.")
        logger.info("To see your account's API Keys, visit your /settings page.")
        logger.info(
            "Then you can use that key by setting the GABLE_API_KEY env var or using the --api-key flag."
        )

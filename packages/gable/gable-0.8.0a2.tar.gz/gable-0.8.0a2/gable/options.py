import functools
import os
import sys
import traceback
from typing import Literal, Optional, get_args

import click
from click_option_group import OptionGroup, optgroup
from gable.client import GableClient
from gable.helpers.logging import configure_debug_logger, configure_trace_logger
from gable.helpers.multi_option import MultiOption
from loguru import logger

gable_api_endpoint = None
gable_api_key = None

DATABASE_SOURCE_TYPE = Literal["postgres", "mysql"]
DATABASE_SOURCE_TYPE_VALUES = list(get_args(DATABASE_SOURCE_TYPE))
FILE_SOURCE_TYPE = Literal["avro", "protobuf", "json_schema"]
FILE_SOURCE_TYPE_VALUES = list(get_args(FILE_SOURCE_TYPE))
PYTHON_SOURCE_TYPE = Literal["python"]  # Add python to the source types
PYTHON_SOURCE_TYPE_VALUES = list(
    get_args(PYTHON_SOURCE_TYPE)
)  # Add python to the source types
SCHEMA_SOURCE_TYPE = Literal[DATABASE_SOURCE_TYPE, FILE_SOURCE_TYPE]
SCHEMA_SOURCE_TYPE_VALUES = list(get_args(SCHEMA_SOURCE_TYPE))
ALL_SOURCE_TYPE = Literal[DATABASE_SOURCE_TYPE, FILE_SOURCE_TYPE, PYTHON_SOURCE_TYPE]
ALL_SOURCE_TYPE_VALUES = list(get_args(ALL_SOURCE_TYPE))


class Context:
    def __init__(self):
        self.client: Optional[GableClient] = None


def create_client_callback(ctx, param, value):
    if param.name == "endpoint":
        global gable_api_endpoint
        gable_api_endpoint = value
    elif param.name == "api_key":
        global gable_api_key
        gable_api_key = value
    if gable_api_endpoint and gable_api_key:
        if ctx.obj is None:
            ctx.obj = Context()
        # Once we've collected both values, create the client
        logger.debug(f"Creating Gable client with endpoint {gable_api_endpoint}")
        ctx.obj.client = GableClient(gable_api_endpoint, gable_api_key)
    return value


def help_option(func):
    """Re-adds the help option, which fixes the eagerness issue with required parameters... Without this, if a parameter
    is marked as required, <command> --help will fail because the required parameters are not provided.
    """

    @click.help_option(is_eager=True)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def endpoint_options(func, global_option_group: OptionGroup):
    """Decorator that adds global endpoint options to a command. This decorator is added by the below global_options
    decorator, so it should not be used directly"""

    @global_option_group.option(
        "--endpoint",
        default=lambda: os.environ.get("GABLE_API_ENDPOINT", ""),
        required=True,
        # Don't pass these values to the subcommand functions
        expose_value=False,
        callback=create_client_callback,
        help="Customer API endpoint for Gable, in the format https://api.company.gable.ai/. Can also be set with the GABLE_API_ENDPOINT environment variable.",
    )
    @global_option_group.option(
        "--api-key",
        default=lambda: os.environ.get("GABLE_API_KEY", ""),
        required=True,
        # Don't pass these values to the subcommand functions
        expose_value=False,
        callback=create_client_callback,
        help="API Key for Gable. Can also be set with the GABLE_API_KEY environment variable.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def logging_options(func, global_option_group: OptionGroup):
    """Decorator that adds global logging options to a command. This decorator is added by the below global_options
    decorator, so it should not be used directly"""

    @global_option_group.option(
        "--debug",
        help="Enable debug logging",
        is_flag=True,
        default=False,
        # Make eager so we can configure logging before the other options are parsed
        is_eager=True,
        # Unintuitive, but we need to set this to true even though we don't actually want to pass this value to the
        # subcommand functions. We need this in the below function wrapper to determine if we should log detailed
        # exception information. This will be stripped out of the kwargs before they are passed to the subcommand
        expose_value=True,
        callback=configure_debug_logger,
    )
    @global_option_group.option(
        "--trace",
        help="Enable trace logging. This is the most verbose logging level and should only be used for debugging.",
        is_flag=True,
        default=False,
        # Make eager so we can configure logging before the other options are parsed
        is_eager=True,
        # Unintuitive, but we need to set this to true even though we don't actually want to pass this value to the
        # subcommand functions. We need this in the below function wrapper to determine if we should log detailed
        # exception information. This will be stripped out of the kwargs before they are passed to the subcommand
        expose_value=True,
        callback=configure_trace_logger,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if debug logging is enabled
        debug_logging_enabled = "debug" in kwargs and kwargs["debug"]
        trace_logging_enabled = "trace" in kwargs and kwargs["trace"]
        # We need to remove the debug/trace flags from the kwargs before passing them to the subcommand functions
        # because they don't expect it
        if "debug" in kwargs:
            del kwargs["debug"]
        if "trace" in kwargs:
            del kwargs["trace"]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if debug_logging_enabled or trace_logging_enabled:
                # If trace logging is enabled, log the full exception information
                if trace_logging_enabled:
                    logger.exception(traceback.format_exc())
                # Otherwise, just log the exception message
                else:
                    logger.exception(str(e))
                # Then immediately exit to prevent the default click exception handler from printing the exception
                # again. If this is a ClickException, grab the exit code and use that, otherwise use 1
                exit_code = e.exit_code if isinstance(e, click.ClickException) else 1
                # The context should always be available here, but just in case it isn't use sys.exit() instead
                context = click.get_current_context(silent=True)
                if context:
                    context.exit(exit_code)
                sys.exit(exit_code)
            # If debug logging is not enabled, just raise the exception and let the default click exception handler
            # print it
            raise e

    return wrapper


def global_options(add_endpoint_options=True):
    """Decorator that adds global options to a command. This decorator should be applied to all commands to add the
    --debug/--trace options, and conditionally (though almost always) add the --endpoint/--api-key options.
    """

    def decorate(func):
        func = help_option(func)
        global_option_group = OptionGroup("Global Options")
        func = logging_options(func, global_option_group)
        if add_endpoint_options:
            # Return the function unchanged, not decorated.
            func = endpoint_options(func, global_option_group)

        return func

    return decorate


def required_option_callback(ctx, param, value):
    """This callback is used to enforce required options when the option needs to be eager, which can cause problems
    with the --help flag"""
    if not value or str(value).strip() == "":
        raise click.MissingParameter(ctx=ctx, param=param)
    return value


def check_for_empty_string_callback(ctx, param, value):
    """This callback is used to check for optional options that were specified, but might be an empty string"""
    if value != None and str(value).strip() == "":
        raise click.BadParameter("Cannot be an empty string", ctx=ctx, param=param)
    return value


def source_type_dependent_required_option_callback(ctx, param, value):
    """This callback is used to conditionally enforce option requirements based on the source type (right now database
    or file). For example, if the source type is a file (protobuf, avro), we want to disable the required options for
    the database source type otherwise the command will fail. Without this callback, we're unable to mark ANY options
    as required.

    This callback requires the --source-type option to be processed first so it's available in the context.
    """

    source_type: ALL_SOURCE_TYPE = ctx.params["source_type"]

    if source_type in DATABASE_SOURCE_TYPE_VALUES:
        # Only require the options for the database source type
        if param.group.name == "Database Options" and not value:
            raise click.MissingParameter(ctx=ctx, param=param)
    elif source_type in FILE_SOURCE_TYPE_VALUES:
        # Only require the options for the file source type
        if param.group.name == "Protobuf & Avro options" and not value:
            raise click.MissingParameter(ctx=ctx, param=param)
    elif source_type in PYTHON_SOURCE_TYPE_VALUES:
        if param.group.name == "Python Project Options" and not value:
            raise click.MissingParameter(ctx=ctx, param=param)
    else:
        # Should never happen, but just in case
        raise click.BadParameter("", ctx=ctx, param=param)
    return value


@logger.catch()
def python_project_options(
    option_group_help_text: str, action: Literal["register", "check"]
):
    """Decorator that adds Python project related options to a command like 'data-asset register'.

    The 'action' option is used to tweak the help text depending on the command being run. If a new value is
    added, make sure it works as {action}ed and {action}ing (e.g. registered and registering, checked and checking)
    """

    def decorator(func):
        @optgroup.group(
            "Python Project Options",
            help=option_group_help_text,
        )
        @optgroup.option(
            "--project-root",
            help="This should be the directory location of the Python project that will be bundled.",
            callback=source_type_dependent_required_option_callback,
            type=str,
        )
        @optgroup.option(
            "--emitter-function",
            help="Name of the emitter function",
            callback=source_type_dependent_required_option_callback,
            type=str,
        )
        @optgroup.option(
            "--emitter-payload-parameter",
            help="Name of the parameter representing the event payload",
            callback=source_type_dependent_required_option_callback,
            type=str,
        )
        @optgroup.option(
            "--event-name-key",
            help="Name of the key in the event payload that identifies the event",
            callback=source_type_dependent_required_option_callback,
            type=str,
        )
        @optgroup.option(
            "--emitter-file-path",
            help="Relative path from the root of the project to the file that contains the emitter function",
            callback=source_type_dependent_required_option_callback,
            type=str,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@logger.catch()
def file_source_type_options(
    option_group_help_text: str, action: Literal["register", "check"]
):
    """Decorator that adds file sour type (protobuf, avro, etc) related options to a command like 'data-asset register'.

    The 'action' option is used to tweak the help text depending on the command being run. If a new value is
    added, make sure it works as {action}ed and {action}ing (e.g. registered and registering, checked and checking)
    """

    def decorator(func):
        @optgroup.group(
            "Protobuf & Avro options",
            help=option_group_help_text,
        )
        @optgroup.option(
            "--files",
            help=f"Space delimited path(s) to the contracts to {action}, with support for glob patterns.",
            type=tuple,
            callback=source_type_dependent_required_option_callback,
            cls=MultiOption,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def proxy_database_options(
    option_group_help_text: str, action: Literal["register", "check"]
):
    """Decorator that adds database + proxy database related options to a command like 'data-asset register'.

    The 'action' option is used to tweak the help text depending on the command being run. If a new value is
    added, make sure it works as {action}ed and {action}ing (e.g. registered and registering, checked and checking)
    """

    def decorator(func):
        @optgroup.group(
            "Database Options",
            help=option_group_help_text,
        )
        @optgroup.option(
            "--host",
            "-h",
            type=str,
            callback=source_type_dependent_required_option_callback,
            help="""The host name of the production database, for example 'service-one.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com'.
            Despite not needing to connect to the production database, the host is still needed to generate the unique resource 
            name for the real database tables (data assets).
            """,
        )
        @optgroup.option(
            "--port",
            "-p",
            type=int,
            callback=source_type_dependent_required_option_callback,
            help="""The port of the production database. Despite not needing to connect to the production database, the port is 
            still needed to generate the unique resource name for the real database tables (data assets).
            """,
        )
        @optgroup.option(
            "--db",
            type=str,
            callback=source_type_dependent_required_option_callback,
            help="""The name of the production database. Despite not needing to connect to the production database, the database 
            name is still needed to generate the unique resource name for the real database tables (data assets).
            
            Database naming convention frequently includes the environment (production/development/test/staging) in the 
            database name, so this value may not match the name of the database in the proxy database instance. If this is 
            the case, you can set the --proxy-db value to the name of the database in the proxy instance, but we'll use the 
            value of --db to generate the unique resource name for the data asset.
            
            For example, if your production database is 'prod_service_one', but your test database is 'test_service_one', 
            you would set --db to 'prod_service_one' and --proxy-db to 'test_service_one'.""",
        )
        @optgroup.option(
            "--schema",
            "-s",
            type=str,
            callback=source_type_dependent_required_option_callback,
            help=f"""The schema of the production database containing the table(s) to {action}. Despite not needing to connect to 
            the production database, the schema is still needed to generate the unique resource name for the real database tables
            (data assets).
            
            Database naming convention frequently includes the environment (production/development/test/staging) in the 
            schema name, so this value may not match the name of the schema in the proxy database instance. If this is 
            the case, you can set the --proxy-schema value to the name of the schema in the proxy instance, but we'll use the 
            value of --schema to generate the unique resource name for the data asset.
            
            For example, if your production schema is 'production', but your test database is 'test', 
            you would set --schema to 'production' and --proxy-schema to 'test'.""",
        )
        @optgroup.option(
            "--table",
            "--tables",
            "-t",
            type=str,
            callback=check_for_empty_string_callback,
            default=None,
            help=f"""A comma delimited list of the table(s) to {action}. If no table(s) are specified, all tables within the provided schema will be {action}ed.

            Table names in the proxy database instance must match the table names in the production database instance, even if
            the database or schema names are different.""",
        )
        @optgroup.option(
            "--proxy-host",
            "-ph",
            type=str,
            callback=source_type_dependent_required_option_callback,
            help=f"""The host string of the database instance that serves as the proxy for the production database. This is the 
            database that Gable will connect to when {action}ing tables in the CI/CD workflow. 
            """,
        )
        @optgroup.option(
            "--proxy-port",
            "-pp",
            type=int,
            callback=source_type_dependent_required_option_callback,
            help=f"""The port of the database instance that serves as the proxy for the production database. This is the 
            database that Gable will connect to when {action}ing tables in the CI/CD workflow. 
            """,
        )
        @optgroup.option(
            "--proxy-db",
            "-pdb",
            type=str,
            callback=check_for_empty_string_callback,
            default=None,
            help="""Only needed if the name of the database in the proxy instance is different than the name of the
            production database. If not specified, the value of --db will be used to generate the unique resource name for 
            the data asset. 
            
            For example, if your production database is 'prod_service_one', but your test database is 'test_service_one', 
            you would set --db to 'prod_service_one' and --proxy-db to 'test_service_one'.
            """,
        )
        @optgroup.option(
            "--proxy-schema",
            "-ps",
            type=str,
            callback=check_for_empty_string_callback,
            default=None,
            help="""Only needed if the name of the schema in the proxy instance is different than the name of the schema in the
            production database. If not specified, the value of --schema will be used to generate the unique resource name for 
            the data asset. 
            
            For example, if your production schema is 'production', but your test database is 'test', you would set --schema to
            'production' and --proxy-schema to 'test'.
            """,
        )
        @optgroup.option(
            "--proxy-user",
            "-pu",
            type=str,
            callback=source_type_dependent_required_option_callback,
            help=f"""The user that will be used to connect to the proxy database instance that serves as the proxy for the production 
            database. This is the database that Gable will connect to when {action}ing tables in the CI/CD workflow. 
            """,
        )
        @optgroup.option(
            "--proxy-password",
            "-ppw",
            type=str,
            default=None,
            help=f"""If specified, the password that will be used to connect to the proxy database instance that serves as the proxy for 
            the production database. This is the database that Gable will connect to when {action}ing tables in the CI/CD workflow. 
            """,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator

import base64
import json
import os
from typing import List, Optional, Union, cast

import click
import requests
import yaml
from click.core import Context as ClickContext
from click_option_group import optgroup
from gable.client import GableClient
from gable.helpers.check import post_data_assets_check_requests
from gable.helpers.data_asset import (
    determine_should_block,
    format_check_data_assets_json_output,
    format_check_data_assets_text_output,
    gather_python_asset_data,
    get_generated_data_asset_contract,
    get_schema_contents,
    get_source_names,
    is_empty_schema_contents,
    post_ingest_data_asset,
)
from gable.helpers.emoji import EMOJI
from gable.helpers.repo_interactions import get_git_repo_info, get_git_ssh_file_path
from gable.openapi import (
    CheckDataAssetCommentMarkdownResponse,
    CheckDataAssetDetailedResponse,
    CheckDataAssetErrorResponse,
    CheckDataAssetNoContractResponse,
    ErrorResponse,
    ResponseType,
)
from gable.options import (
    ALL_SOURCE_TYPE_VALUES,
    DATABASE_SOURCE_TYPE_VALUES,
    FILE_SOURCE_TYPE_VALUES,
    PYTHON_SOURCE_TYPE_VALUES,
    SCHEMA_SOURCE_TYPE_VALUES,
    file_source_type_options,
    gable_api_key,
    global_options,
    proxy_database_options,
    python_project_options,
    required_option_callback,
)
from gable.readers.file import read_file
from loguru import logger
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(name="data-asset")
def data_asset():
    """Commands for data assets"""


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="list",
)
@click.pass_context
@click.option(
    "-o",
    "--output",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Format of the output. Options are: table (default) or json",
)
@click.option(
    "--full",
    is_flag=True,
    help="Return full data asset details including namespace and name",
)
@global_options()
def list_data_assets(ctx: ClickContext, output: str, full: bool) -> None:
    """List all data assets"""
    # Get the data
    response, success, status_code = ctx.obj.client.get("v0/data-assets")

    # Format the output
    if output == "json":
        data_asset_list = []
        for data_asset in response:
            row = {"resourceName": f"{data_asset['namespace']}:{data_asset['name']}"}
            if full:
                # Filter out invalid data assets...
                if "://" in data_asset["namespace"]:
                    row["type"] = data_asset["namespace"].split("://", 1)[0]
                    row["dataSource"] = data_asset["namespace"].split("://", 1)[1]
                    row["name"] = data_asset["name"]
            data_asset_list.append(row)
        logger.info(json.dumps(data_asset_list))
    else:
        table = Table(show_header=True, title="Data Assets")
        table.add_column("resourceName")
        if full:
            table.add_column("type")
            table.add_column("dataSource")
            table.add_column("name")
        for data_asset in response:
            if not full:
                table.add_row(f"{data_asset['namespace']}:{data_asset['name']}")
            else:
                # Filter out invalid data assets...
                if "://" in data_asset["namespace"]:
                    table.add_row(
                        f"{data_asset['namespace']}:{data_asset['name']}",
                        data_asset["namespace"].split("://", 1)[0],
                        data_asset["namespace"].split("://", 1)[1],
                        data_asset["name"],
                    )
        console.print(table)


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="register",
    epilog="""Example:

gable data-asset register --source-type postgres \\
    --host prod.pg.db.host --port 5432 --db transit --schema public --table routes \\
    --proxy-host localhost --proxy-port 5432 --proxy-user root --proxy-password password""",
)
@click.pass_context
@click.option(
    "--source-type",
    callback=required_option_callback,
    is_eager=True,
    type=click.Choice(list(ALL_SOURCE_TYPE_VALUES), case_sensitive=True),
    help="""The type of data asset.
    
    For databases (postgres, mysql) a data asset is a table within the database.

    For protobuf/avro/json_schema a data asset is message/record/schema within a file.
    """,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without actually registering the data asset.",
    default=False,
)
@proxy_database_options(
    option_group_help_text="""Options for registering database tables as data assets. Gable relies on having a proxy database that mirrors your 
    production database, and will connect to the proxy database to register tables as data assets. This is to ensure that 
    Gable does not have access to your production data, or impact the performance of your production database in any way. 
    The proxy database can be a local Docker container, a Docker container that is spun up in your CI/CD workflow, or a
    database instance in a test/staging environment. The tables in the proxy database must have the same schema as your 
    production database for all tables to be correctly registered. The proxy database must be accessible from the 
    machine that you are running the gable CLI from.

    If you're registering tables in your CI/CD workflow, it's important to only register from the main branch, otherwise 
    you may end up registering tables that do not end up in production.
    """,
    action="register",
)
@file_source_type_options(
    option_group_help_text="""Options for registering a Protobuf message, Avro record, or JSON schema object as data assets. These objects 
    represent data your production services produce, regardless of the transport mechanism. 

    If you're registering Protobuf messages, Avro records, or JSON schema objects in your CI/CD workflow, it's important 
    to only register from the main branch, otherwise you may end up registering records that do not end up in production.
    """,
    action="register",
)
@python_project_options(
    option_group_help_text="""
    Options for registering Python projects as data assets. This set of options is designed to handle the registration of Python-based projects, 
    enabling Gable to track and manage Python codebases as part of its data asset inventory.

    When registering a Python project, it's important to specify the project's entry point, which is the root directory of your project. 
    This allows Gable to correctly identify and bundle the project for analysis. Additionally,
    specifying the emitter function and event name key helps Gable understand how your project interacts with and emits data, 
    ensuring accurate tracking and management.

    The Python project options include:
    - Specifying the project's entry point for proper bundling.
    - Identifying the emitter function to track how the project emits data.
    - Defining the event name key for targeted event handling and listening.

    It's crucial to ensure that the information provided reflects the actual state of your project in your production environment. 
    When using these options as part of your CI/CD workflow, make sure to register your Python projects from the main branch. 
    Registering from feature or development branches may lead to inconsistencies and inaccuracies in the data asset registry, 
    as these branches may contain code that is not yet, or may never be, deployed to production.
    """,
    action="register",
)
@global_options()
def register_data_asset(
    ctx: ClickContext,
    source_type: str,
    dry_run: bool,
    host: str,
    port: int,
    db: str,
    schema: str,
    table: Union[str, None],
    proxy_host: str,
    proxy_port: int,
    proxy_db: str,
    proxy_schema: str,
    proxy_user: str,
    proxy_password: str,
    files: tuple,
    project_root: Optional[str],
    emitter_function: Optional[str],
    emitter_payload_parameter: Optional[str],
    event_name_key: Optional[str],
    emitter_file_path: Optional[str],
) -> None:
    """Registers a data asset with Gable"""
    tables: list[str] | None = [t.strip() for t in table.split(",")] if table else None
    if source_type in DATABASE_SOURCE_TYPE_VALUES:
        proxy_db = proxy_db if proxy_db else db
        proxy_schema = proxy_schema if proxy_schema else schema
        files_list: list[str] = []
        database_schema = f"{db}.{schema}"
    elif source_type in PYTHON_SOURCE_TYPE_VALUES:
        files_list: list[str] = []
        database_schema = ""
    else:
        # Turn the files tuple into a list
        files_list: list[str] = list(files)
        # This won't be set for file-based data assets, but we need to pass through
        # the real db.schema value in case the proxy database has different names
        database_schema = ""
    # This won't be set for file-based data assets, but we need to pass through
    # the real db.schema value in case the proxy database has different names
    temp_upload_key = None
    temp_encryption_key = None

    source_names: list[str] = []
    schema_contents: list[str] = []
    client: GableClient = ctx.obj.client
    if source_type in SCHEMA_SOURCE_TYPE_VALUES:
        schema_contents = get_schema_contents(
            source_type=source_type,
            dbuser=proxy_user,
            dbpassword=proxy_password,
            db=proxy_db,
            dbhost=proxy_host,
            dbport=proxy_port,
            schema=proxy_schema if proxy_schema else schema,
            tables=tables,
            files=files_list,
        )
        source_names = get_source_names(
            ctx=ctx,
            source_type=source_type,
            dbhost=host,
            dbport=port,
            files=files_list,
        )
    elif source_type in PYTHON_SOURCE_TYPE_VALUES:
        if project_root:
            (
                temp_upload_key,
                temp_encryption_key,
                schema_contents,
                source_names,
            ) = gather_python_asset_data(
                project_root,
                emitter_file_path,  # type: ignore
                ctx.params.get("debug", False),
                ctx.obj.client,
            )
        else:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} You must provide the project root for Python-based data assets."
            )
        # Get the lambda function url, which we'll use for the call to the ingest endpoint
        # so we can workaround the API Gateway's short timeout
        lurl_response, lurl_success, lurl_status_code = ctx.obj.client.get(
            "v0/lambda-url"
        )
        if not lurl_success or lurl_status_code != requests.codes.ok:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to get lambda URL: {lurl_status_code}"
            )
        # Create a new client with the lambda URL
        client = GableClient(lurl_response["endpoint"], ctx.obj.client.api_key)
    else:
        raise NotImplementedError(f"Unknown source type: {source_type}")
    if is_empty_schema_contents(source_type, schema_contents):
        raise click.ClickException(
            f"{EMOJI.RED_X.value} No data assets found found to register! You can use the --debug or --trace flags for more details.",
        )
    if dry_run:
        logger.info("Dry run mode. Data asset registration not performed.")
    # Send the schemas to Gable
    response, success, status_code = post_ingest_data_asset(
        client,
        source_type,
        source_names,
        database_schema,
        schema_contents,
        temp_upload_key,
        temp_encryption_key,
        dry_run,
        emitter_function,
        emitter_payload_parameter,
        event_name_key,
        emitter_file_path,
    )
    if not success:
        raise click.ClickException(
            f"{EMOJI.RED_X.value} Registration failed for some data assets: {str(response)}"
        )
    logger.info(
        f"{EMOJI.GREEN_CHECK.value} Registration successful: {response['registered']}"
    )
    logger.info(response["message"])


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="check",
    epilog="""Example:

gable data-asset check --source-type protobuf --files ./**/*.proto""",
)
@click.pass_context
@click.option(
    "--source-type",
    required=True,
    type=click.Choice(ALL_SOURCE_TYPE_VALUES, case_sensitive=True),
    help="""The type of data asset.
    
    For databases (postgres, mysql) the check will be performed for all tables within the database.

    For protobuf/avro/json_schema the check will be performed for all file(s)
    """,
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Format of the output. Options are: text (default), json, or markdown which is intended to be used as a PR comment",
)
@proxy_database_options(
    option_group_help_text="""Options for checking contract compliance for tables in a relational database. The check will be performed
    for any tables that have a contract associated with them.
    
    Gable relies on having a proxy database that mirrors your production database, and will connect to the proxy database
    to perform the check in order to perform the check as part of the CI/CD process before potential changes in the PR are
    merged.
    """,
    action="check",
)
@file_source_type_options(
    option_group_help_text="""Options for checking Protobuf message(s), Avro record(s), or JSON schema object(s) for contract violations.""",
    action="check",
)
@python_project_options(
    option_group_help_text="""
    Options for checking contract compliance for assets emitted in Python project code. This set of options mirrors the registration options, and will
    perform a check for any assets that have a contract associated with them.
    """,
    action="check",
)
@global_options()
def check_data_asset(
    ctx: ClickContext,
    source_type: str,
    output: str,
    host: str,
    port: int,
    db: str,
    schema: str,
    table: str,
    proxy_host: str,
    proxy_port: int,
    proxy_db: str,
    proxy_schema: str,
    proxy_user: str,
    proxy_password: str,
    files: tuple,
    project_root: str,
    emitter_function: str,
    emitter_payload_parameter: str,
    event_name_key: str,
    emitter_file_path: str,
) -> None:
    """Checks data asset(s) against a contract"""
    # Standardize the source type
    tables: list[str] | None = [t.strip() for t in table.split(",")] if table else None

    temp_upload_key = None
    temp_encryption_key = None
    schema_contents = []
    source_names = []
    temp_upload_key = None
    temp_encryption_key = None
    client = ctx.obj.client
    if source_type in PYTHON_SOURCE_TYPE_VALUES:
        if project_root:
            (
                temp_upload_key,
                temp_encryption_key,
                schema_contents,
                source_names,
            ) = gather_python_asset_data(
                project_root,
                emitter_file_path,  # type: ignore
                ctx.params.get("debug", False),
                ctx.obj.client,
            )
        else:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} You must provide the project root for Python-based data assets."
            )
        # Get the lambda function url, which we'll use for the call to the ingest endpoint
        # so we can workaround the API Gateway's short timeout
        lurl_response, lurl_success, lurl_status_code = ctx.obj.client.get(
            "v0/lambda-url"
        )
        if not lurl_success or lurl_status_code != requests.codes.ok:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to get lambda URL: {lurl_status_code}"
            )
        # Create a new client with the lambda URL
        client = GableClient(lurl_response["endpoint"], ctx.obj.client.api_key)
    elif (
        source_type in SCHEMA_SOURCE_TYPE_VALUES
        or source_type in FILE_SOURCE_TYPE_VALUES
    ):
        schema_contents = get_schema_contents(
            source_type=source_type,
            dbuser=proxy_user,
            dbpassword=proxy_password,
            db=proxy_db or db,
            dbhost=proxy_host,
            dbport=proxy_port,
            schema=proxy_schema or schema,
            tables=tables,
            files=[] if files is None else list(files),
        )
        source_names = get_source_names(
            ctx=ctx,
            source_type=source_type,
            dbhost=host,
            dbport=port,
            files=[] if files is None else list(files),
        )

    if is_empty_schema_contents(source_type, schema_contents):
        raise click.ClickException(
            f"{EMOJI.RED_X.value} No data assets found found to check! You can use the --debug or --trace flags for more details."
        )
    response_type = (
        ResponseType.COMMENT_MARKDOWN if output == "markdown" else ResponseType.DETAILED
    )

    # Send the schemas to Gable, and get the results
    results = post_data_assets_check_requests(
        client,
        response_type,
        source_type,
        source_names,
        db,
        schema,
        schema_contents,
        emitter_function,
        emitter_payload_parameter,
        event_name_key,
        emitter_file_path,
        temp_upload_key,
        temp_encryption_key,
    )
    if isinstance(results, ErrorResponse):
        raise click.ClickException(
            f"Error checking data asset(s): {results.title} ({results.id})\n\t{results.message}"
        )
    # If the output was text, or json
    if output == "text" or output == "json":
        # Cast to list of detailed responses
        results = cast(
            list[
                CheckDataAssetDetailedResponse
                | CheckDataAssetErrorResponse
                | CheckDataAssetNoContractResponse
            ],
            results,
        )
        # Determine if we should block (non-zero exit code) or not
        should_block = determine_should_block(results)
        if output == "text":
            # Format the results
            output_string = format_check_data_assets_text_output(results)
        else:
            output_string = format_check_data_assets_json_output(results)

        if should_block:
            logger.info(output_string)
            raise click.ClickException("Contract violation(s) found")
        else:
            logger.info(output_string)
    else:
        # If the output was markdown
        results = cast(CheckDataAssetCommentMarkdownResponse, results)
        # Only print the markdown if it's not None or empty, otherwise the stdout will contain a newline. Print markdown
        # to stdout, so we can read it separately from the error output to determine if we should comment on a PR
        if results.markdown and results.markdown != "":
            logger.info(results.markdown)
        # Decide if we should comment on or block the PR based on whether or not there were any contract violations, and the
        # enforcement level of the contacts that had the violations. In either case, write something to stderr so there's
        # a record logged in the CI/CD output
        if results.shouldBlock:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Contract violations found, maximum enforcement level was 'BLOCK'"
            )
        elif results.shouldAlert:
            logger.error(
                f"{EMOJI.YELLOW_WARNING.value} Contract violations found, maximum enforcement level was 'ALERT'"
            )
        # If there were errors
        if results.errors:
            errors_string = "\n".join(
                [json.dumps(error.dict()) for error in results.errors]
            )
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Contract checking failed for some data assets:\n{errors_string}"
            )


@data_asset.command(
    name="create-contract",
    epilog="""Example:
                    
gable data-asset create-contract --data-asset-id postgres://sample.host:5432:db.public.table --output-dir contracts""",
)
@click.pass_context
@click.argument(
    "data_asset_ids",
    nargs=-1,
)
@click.option(
    "--output-dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    help="Directory to output contracts. This directory must exist",
)
def create_data_asset_contracts(
    ctx: ClickContext, data_asset_ids: List[str], output_dir: Optional[str]
) -> None:
    """Creates the YAML contract specification for a list of data assets

    The specification that is produced is based off the registered data asset but the
    user will need to fill in places marked with 'PLACEHOLDER:' such as field
    descriptions and ownership information.
    """
    for data_asset_id in data_asset_ids:
        logger.debug(f"Creating contract for data asset: {data_asset_id}")

        # Base64 encode the data asset ID
        encoded_resource_name = base64.b64encode(data_asset_id.encode("utf-8")).decode(
            "utf-8"
        )

        # Get the inferred contract for the data asset
        response, success, status_code = get_generated_data_asset_contract(
            ctx.obj.client, encoded_resource_name
        )
        if not success:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to generate contract for data asset: {data_asset_id} ({status_code}))"
            )

        # Get the raw contract spec and convert to yaml
        contract_spec_dict = json.loads(response["contractSpecRaw"])
        contract_spec_yaml = yaml.dump(
            contract_spec_dict, default_flow_style=False, sort_keys=False
        )

        # Print out the data asset
        logger.info(contract_spec_yaml)

        if output_dir:
            # Get the contract name for the filename
            name = response["contractSpec"]["name"].lower().replace(".", "_")
            filepath = os.path.join(output_dir, f"{name}.yaml")

            # Write the contract spec to a file
            with open(filepath, "w") as f:
                f.write(contract_spec_yaml)

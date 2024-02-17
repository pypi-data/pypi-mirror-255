import json
import os
from pathlib import Path
from typing import Any, List, Optional, Tuple, cast

import click
import jsonref
import requests
from gable.client import GableClient
from gable.helpers.bundler import encrypt_gzip_payload, get_bundled_project
from gable.helpers.emoji import EMOJI
from gable.helpers.repo_interactions import get_git_repo_info, get_git_ssh_file_path
from gable.openapi import (
    CheckDataAssetDetailedResponse,
    CheckDataAssetErrorResponse,
    CheckDataAssetNoContractResponse,
    EnforcementLevel,
)
from gable.options import DATABASE_SOURCE_TYPE_VALUES
from gable.readers.dbapi import DbapiReader
from gable.readers.file import read_file
from loguru import logger


def standardize_source_type(source_type: str) -> str:
    return source_type.lower()


def validate_db_input_args(user: str, password: str, db: str) -> None:
    if user is None:
        raise ValueError("User (--proxy-user) is required for database connections")
    if password is None:
        raise ValueError(
            "Password (--proxy-password) is required for database connections"
        )
    if db is None:
        raise ValueError("Database (--proxy-db) is required for database connections")


def get_db_connection(
    source_type: str, user: str, password: str, db: str, host: str, port: int
):
    if source_type == "postgres":
        try:
            from gable.readers.postgres import create_postgres_connection

            return create_postgres_connection(user, password, db, host, port)
        except ImportError:
            raise ImportError(
                "The psycopg2 library is not installed. Run `pip install 'gable[postgres]'` to install it."
            )
    elif source_type == "mysql":
        try:
            from gable.readers.mysql import create_mysql_connection

            return create_mysql_connection(user, password, db, host, port)
        except ImportError:
            raise ImportError(
                "The MySQLdb library is not installed. Run `pip install 'gable[mysql]'` to install it."
            )


def get_db_schema_contents(
    source_type: str, connection: Any, schema: str, tables: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    reader = DbapiReader(connection=connection)
    return reader.get_information_schema(
        source_type=source_type, schema=schema, tables=tables
    )


def get_db_resource_name(
    source_type: str, host: str, port: int, db: str, schema: str, table: str
) -> str:
    return f"{source_type}://{host}:{port}/{db}/{schema}/{table}"


def get_protobuf_resource_name(source_type: str, namespace: str, message: str) -> str:
    return f"{source_type}://{namespace}/{message}"


def get_avro_resource_name(source_type: str, namespace: str, record: str) -> str:
    return f"{source_type}://{namespace}/{record}"


def get_schema_contents(
    source_type: str,
    dbuser: str,
    dbpassword: str,
    db: str,
    dbhost: str,
    dbport: int,
    schema: str,
    tables: Optional[list[str]],
    files: list[str],
) -> list[str]:
    # Validate the source type arguments and get schema contents
    if source_type in ["postgres", "mysql"]:
        validate_db_input_args(dbuser, dbpassword, db)
        connection = get_db_connection(
            source_type, dbuser, dbpassword, db, dbhost, dbport
        )
        return [
            json.dumps(
                get_db_schema_contents(source_type, connection, schema, tables=tables)
            )
        ]
    elif source_type in ["avro", "protobuf", "json_schema"]:
        schema_contents: list[str] = []
        for file in files:
            if source_type == "json_schema":
                file_path = Path(file).absolute()

                try:
                    # Resolve any local JSON references before sending the schema
                    with file_path.open() as file_contents:
                        result = jsonref.load(
                            file_contents,
                            base_uri=file_path.as_uri(),
                            jsonschema=True,
                            proxies=False,
                        )
                        schema_contents.append(jsonref.dumps(result))
                except Exception as exc:
                    # Log full stack trace with --debug flag
                    logger.opt(exception=exc).debug(
                        f"{file}: Error parsing JSON Schema file, or resolving local references: {exc}"
                    )
                    raise click.ClickException(
                        f"{file}: Error parsing JSON Schema file, or resolving local references: {exc}"
                    ) from exc
            else:
                schema_contents.append(read_file(file))
    else:
        raise NotImplementedError(f"Unknown source type: {source_type}")
    return schema_contents


def get_source_names(
    ctx: click.Context,
    source_type: str,
    dbhost: str,
    dbport: int,
    files: list[str],
) -> list[str]:
    # Validate the source type arguments and get schema contents
    if source_type in ["postgres", "mysql"]:
        return [f"{dbhost}:{dbport}"]
    elif source_type in ["avro", "protobuf", "json_schema"]:
        source_names = []
        for file in files:
            source_names.append(get_git_ssh_file_path(get_git_repo_info(file), file))
        return source_names
    else:
        raise NotImplementedError(f"Unknown source type: {source_type}")


def del_none(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.
    """
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d


def post_ingest_data_asset(
    client: GableClient,
    source_type: str,
    source_names: list[str],
    database_schema: str,
    schema_contents: list[str],
    temp_upload_key: Optional[str] = None,
    temp_encryption_key: Optional[str] = None,
    dry_run: bool = False,
    emitter_function: Optional[str] = None,
    emitter_payload_parameter: Optional[str] = None,
    event_name_key: Optional[str] = None,
    emitter_file_path: Optional[str] = None,
) -> tuple[dict[str, Any], bool, int]:
    def request_log_filter(json_payload):
        # gzipPayload is base64 encoded .tar.gz, not useful in log output
        if json_payload and "gzipPayload" in json_payload:
            del json_payload["gzipPayload"]
        if json_payload and "decryptionKey" in json_payload:
            json_payload["decryptionKey"] = "****************"
        return json_payload

    request = {
        "sourceType": source_type,
        "sourceNames": source_names,
        "databaseSchema": database_schema,
        "schema": schema_contents,
        "dryRun": dry_run,
        "emitterFunction": emitter_function,
        "emitterFunctionPayloadParameter": emitter_payload_parameter,
        "eventNameKey": event_name_key,
        "emitterFilePath": emitter_file_path,
        "uploadKey": temp_upload_key,
        "decryptionKey": temp_encryption_key,
    }
    result, success, status_code = client.post(
        "v0/data-asset/ingest",
        json=del_none(request),
        log_payload_filter=request_log_filter,
    )
    return cast(dict[str, Any], result), success, status_code


def is_empty_schema_contents(
    source_type: str,
    schema_contents: list[str],
) -> bool:
    if len(schema_contents) == 0 or (
        # If we're registering a database table the schema_contents array will contain
        # a stringified empty array, so we need to check for that
        source_type in DATABASE_SOURCE_TYPE_VALUES
        and len(schema_contents) == 1
        and schema_contents[0] == "[]"  # type: ignore
    ):
        return True
    return False


def get_generated_data_asset_contract(
    client: GableClient, data_asset_id: str
) -> tuple[dict[str, Any], bool, int]:
    """Use the infer contract endpoint to generate a contract for a data asset"""
    response, success, status_code = client.get(
        f"v0/data-asset/{data_asset_id}/infer-contract"
    )
    return cast(dict[str, Any], response), success, status_code


def determine_should_block(
    check_data_assets_results: list[
        CheckDataAssetDetailedResponse
        | CheckDataAssetErrorResponse
        | CheckDataAssetNoContractResponse
    ],
) -> bool:
    """For detailed response from the /data-assets/check endpoint, determine if any of the contracts
    have violations and have their enforcement level set to BLOCK.
    """

    for result in check_data_assets_results:
        if isinstance(result, CheckDataAssetDetailedResponse):
            if result.violations is not None and len(result.violations) > 0:
                if result.enforcementLevel == EnforcementLevel.BLOCK:
                    return True
    return False


def format_check_data_assets_text_output(
    check_data_assets_results: list[
        CheckDataAssetDetailedResponse
        | CheckDataAssetErrorResponse
        | CheckDataAssetNoContractResponse
    ],
) -> str:
    """Format the console output for the gable data-asset check command with the '--output text' flag.
    Returns the full command output string.
    """
    results_strings = []
    contract_violations_found = False
    for result in check_data_assets_results:
        if isinstance(result, CheckDataAssetDetailedResponse):
            # If there were violations, print them
            if result.violations is not None and len(result.violations) > 0:
                contract_violations_found = True
                violations_string = "\n\t".join(
                    [
                        f"{violation.field}: {violation.message}\n\tExpected: {violation.expected}\n\tActual: {violation.actual}"
                        for violation in result.violations
                    ]
                )
                results_strings.append(
                    f"{EMOJI.RED_X.value} {result.dataAssetPath}:{violations_string}"
                )
            else:
                # For valid contracts, just print the check mark and name
                results_strings.append(
                    f"{EMOJI.GREEN_CHECK.value} {result.dataAssetPath}: No contract violations found"
                )
        elif isinstance(result, CheckDataAssetErrorResponse):
            # If there was an error, print the error message
            results_strings.append(
                f"{EMOJI.RED_X.value} {result.dataAssetPath}:\n\t{result.message}"
            )
        elif isinstance(result, CheckDataAssetNoContractResponse):
            # For missing contracts print a warning
            results_strings.append(
                f"{EMOJI.YELLOW_WARNING.value} {result.dataAssetPath}: No contract found"
            )
    return (
        "\n".join(results_strings)
        + "\n\n"
        + (
            "Contract violation(s) found"
            if contract_violations_found
            else "No contract violations found"
        )
    )


def format_check_data_assets_json_output(
    check_data_assets_results: list[
        CheckDataAssetDetailedResponse
        | CheckDataAssetErrorResponse
        | CheckDataAssetNoContractResponse
    ],
) -> str:
    """Format the console output for the gable data-asset check command with the '--output json' flag.
    Returns the full command output string.
    """
    # Convert the results to dicts by calling Pydantic's json() on each result to deal with enums, which
    # aren't serializable by default
    results_dict = [json.loads(result.json()) for result in check_data_assets_results]
    return json.dumps(results_dict, indent=4, sort_keys=True)


def gather_python_asset_data(
    project_root: str, emitter_file_path: str, debug_mode: bool, client: Any
) -> Tuple[str, str, List[str], List[str]]:
    """Gathers the gzip_payload, schema_contents, and source_name for a Python-based data asset."""
    project_name = os.path.basename(os.path.abspath(project_root))
    gzip_payload = get_bundled_project(project_root, debug_mode)
    if gzip_payload is not None:
        gzip_payload.seek(0)
        gzip_payload, temp_encryption_key = encrypt_gzip_payload(gzip_payload)
        # Get an S3 url to upload the payload to
        response, success, status_code = client.get("v0/data-asset/ingest")
        if status_code != 200:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to get ingest url: {status_code}"
            )
        response = cast(dict[str, str], response)
        temp_upload_url = response["tempUploadUrl"]
        temp_upload_key = response["key"]
        # Upload the payload
        upload_response = requests.put(
            temp_upload_url,
            headers={"Content-Type": "application/x-gzip"},
            data=gzip_payload,
        )
        if upload_response.status_code != 200:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to upload payload: {upload_response.status_code}"
            )
        logger.debug(
            f"{project_name} project bundled successfully, starting static code analysis..."
        )
        return (
            temp_upload_key,
            temp_encryption_key,
            [project_name],
            [
                get_git_ssh_file_path(
                    get_git_repo_info(project_root + "/" + emitter_file_path),
                    project_root,
                )
            ],
        )
    else:
        raise click.ClickException(
            f"{EMOJI.RED_X.value} Failed to bundle project: {project_name}"
        )

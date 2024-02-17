import json
from typing import Annotated, Any, List, Optional, Union, cast

import click
from gable.client import GableClient
from gable.helpers.data_asset import del_none
from gable.openapi import (
    CheckDataAssetCommentMarkdownResponse,
    CheckDataAssetDetailedResponse,
    CheckDataAssetErrorResponse,
    CheckDataAssetNoContractResponse,
    CheckDataAssetRequest,
    CheckDataAssetsRequest,
    ErrorResponse,
    Input,
    ResponseType,
)
from gable.options import DATABASE_SOURCE_TYPE_VALUES, FILE_SOURCE_TYPE_VALUES
from gable.readers.dbapi import DbapiReader
from gable.readers.file import read_file
from pydantic import Field, parse_obj_as

# Discriminated union for the response from the /data-assets/check endpoint
CheckDataAssetDetailedResponseUnion = Annotated[
    Union[
        CheckDataAssetDetailedResponse,
        CheckDataAssetErrorResponse,
        CheckDataAssetNoContractResponse,
    ],
    Field(discriminator="responseType"),
]


def post_contract_check_request(
    client: GableClient,
    contract_id: str,
    source_type: str,
    schema_contents: str,
) -> tuple[str, bool]:
    result, success, status_code = client.post(
        f"v0/contract/{contract_id}/check",
        json={
            "sourceType": source_type,
            "schemaContents": schema_contents,
        },
    )
    return str(cast(dict[str, Any], result)["message"]), success


def post_data_assets_check_requests(
    client: GableClient,
    responseType: ResponseType,
    source_type: str,
    source_names: List[str],
    realDbName: str,
    realDbSchema: str,
    schema_contents: List[str],
    emitter_function: Optional[str] = None,
    emitter_payload_parameter: Optional[str] = None,
    event_name_key: Optional[str] = None,
    emitter_file_path: Optional[str] = None,
    temp_upload_key: Optional[str] = None,
    temp_decrypt_key: Optional[str] = None,
) -> Union[
    ErrorResponse,
    CheckDataAssetCommentMarkdownResponse,
    list[
        Union[
            CheckDataAssetDetailedResponse,
            CheckDataAssetErrorResponse,
            CheckDataAssetNoContractResponse,
        ]
    ],
]:
    requests = get_check_data_asset_requests(
        source_type=source_type,
        source_names=source_names,
        schema_contents=schema_contents,
        realDbName=realDbName,
        realDbSchema=realDbSchema,
        emitter_function=emitter_function,
        emitter_payload_parameter=emitter_payload_parameter,
        event_name_key=event_name_key,
        emitter_file_path=emitter_file_path,
        temp_upload_key=temp_upload_key,
        temp_decrypt_key=temp_decrypt_key,
    )

    inputs = [del_none(input) for input in requests.values()]
    request = {
        "responseType": responseType.value,
        "inputs": inputs,
    }

    result, success, status_code = client.post(
        "v0/data-assets/check",
        json=del_none(request),
    )
    if responseType == ResponseType.DETAILED:
        if type(result) == list:
            return [
                parse_obj_as(
                    CheckDataAssetDetailedResponse
                    | CheckDataAssetErrorResponse
                    | CheckDataAssetNoContractResponse,
                    r,
                )
                for r in result
            ]
        else:
            return ErrorResponse.parse_obj(result)
    else:
        return parse_obj_as(
            CheckDataAssetCommentMarkdownResponse | ErrorResponse, result
        )


def get_check_data_asset_requests(
    source_type: str,
    source_names: list[str],
    schema_contents: list[str],
    realDbName: Optional[str] = None,
    realDbSchema: Optional[str] = None,
    emitter_function: Optional[str] = None,
    emitter_payload_parameter: Optional[str] = None,
    event_name_key: Optional[str] = None,
    emitter_file_path: Optional[str] = None,
    temp_upload_key: Optional[str] = None,
    temp_decrypt_key: Optional[str] = None,
) -> dict[str, dict]:
    requests: dict[str, dict] = {}
    # If this is a database, there might be multiple table's schemas within the information schema
    # returned from the DbApi reader. In that case, we need to post each table's schema separately.
    if source_type in DATABASE_SOURCE_TYPE_VALUES:
        schema_contents_str = schema_contents[0]
        source_name = source_names[0]
        information_schema = json.loads(schema_contents_str)
        grouped_table_schemas: dict[str, List[Any]] = {}
        for information_schema_row in information_schema:
            if information_schema_row["TABLE_NAME"] not in grouped_table_schemas:
                grouped_table_schemas[information_schema_row["TABLE_NAME"]] = []
            grouped_table_schemas[information_schema_row["TABLE_NAME"]].append(
                information_schema_row
            )
        for table_name, table_schema in grouped_table_schemas.items():
            requests[f"{realDbName}.{realDbSchema}.{table_name}"] = {
                "sourceType": source_type,
                "sourceName": source_name,
                "realDbName": realDbName,
                "realDbSchema": realDbSchema,
                "schemaContents": json.dumps(table_schema),
                # can remove following extra fields after https://github.com/koxudaxi/datamodel-code-generator/issues/1827
                "emitterFunction": emitter_function,
                "emitterFunctionPayloadParameter": emitter_payload_parameter,
                "eventNameKey": event_name_key,
                "emitterFilePath": emitter_file_path,
                "uploadKey": temp_upload_key,
                "decryptionKey": temp_decrypt_key,
            }
    elif source_type in FILE_SOURCE_TYPE_VALUES:
        for source_name, schema in zip(source_names, schema_contents):
            requests[source_name] = {
                "sourceType": source_type,
                "sourceName": source_name,
                "schemaContents": schema,
                # can remove following extra fields after https://github.com/koxudaxi/datamodel-code-generator/issues/1827
                "emitterFunction": emitter_function,
                "emitterFunctionPayloadParameter": emitter_payload_parameter,
                "eventNameKey": event_name_key,
                "emitterFilePath": emitter_file_path,
                "uploadKey": temp_upload_key,
                "decryptionKey": temp_decrypt_key,
            }
    else:  # source_type in PYTHON_SOURCE_TYPE_VALUES
        requests[source_names[0]] = {
            "sourceType": source_type,
            "sourceName": source_names[0],
            "schemaContents": schema_contents[0],
            "emitterFunction": emitter_function,
            "emitterFunctionPayloadParameter": emitter_payload_parameter,
            "eventNameKey": event_name_key,
            "emitterFilePath": emitter_file_path,
            "uploadKey": temp_upload_key,
            "decryptionKey": temp_decrypt_key,
        }
    return requests

from typing import List

import click
from click.core import Context as ClickContext
from gable.helpers.check import post_contract_check_request
from gable.helpers.contract import contract_files_to_post_contract_request
from gable.helpers.data_asset import get_schema_contents
from gable.helpers.emoji import EMOJI
from gable.helpers.shell_output import shell_linkify
from gable.options import global_options
from loguru import logger


@click.group()
def contract():
    """Validate/publish contracts and check data asset compliance"""


@contract.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    epilog="""Examples:

    gable contract publish contract1.yaml

    gable contract publish **/*.yaml""",
)
@click.argument(
    "contract_files",
    type=click.File(),
    nargs=-1,
)
@global_options()
@click.pass_context
def publish(ctx: ClickContext, contract_files: List[click.File]):
    """Publishes data contracts to Gable"""
    request = contract_files_to_post_contract_request(contract_files)
    response, success, status_code = ctx.obj.client.post(
        "v0/contract", data=request.json()
    )
    if not success:
        raise click.ClickException(f"Publish failed: {response['message']}")
    updated_contracts = ", ".join(
        shell_linkify(
            f"{ctx.obj.client.ui_endpoint}/contracts/{cid}",
            cid,
        )
        for cid in response["contractIds"]
    )
    if len(response["contractIds"]) == 0:
        logger.info("\u2705 No contracts published")
    else:
        logger.info(f"\u2705 {len(response['contractIds'])} contract(s) published")
        logger.info(f"\t{updated_contracts}")


@contract.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    epilog="""Examples:\n
\b
  gable contract validate contract1.yaml
  gable contract validate **/*.yaml""",
)
@click.argument("contract_files", type=click.File(), nargs=-1)
@click.pass_context
@global_options()
def validate(ctx: ClickContext, contract_files: List[click.File]):
    """Validates the configuration of the data contract files"""
    request = contract_files_to_post_contract_request(contract_files)
    response, success, _status_code = ctx.obj.client.post(
        "v0/contract/validate", data=request.json()
    )
    # For each input file, zip up the emoji, file name, and result message into a tuple
    zipped_results = zip(
        [
            # Compute emoji based on whether the contract is valid
            EMOJI.GREEN_CHECK.value if m.strip() == "VALID" else EMOJI.RED_X.value
            for m in response["message"]
        ],
        contract_files,
        [m.replace("\n", "\n\t") for m in response["message"]],
    )
    string_results = "\n".join(
        [
            # For valid contracts, just print the check mark and name
            f"{x[0]} {x[1].name}" if x[2].strip() == "VALID"
            # For invalid contracts, print the check mark, name, and error message
            else f"{x[0]} {x[1].name}:\n\t{x[2]}"
            for x in zipped_results
        ]
    )
    if not success:
        raise click.ClickException(f"\n{string_results}\nInvalid contract(s)")
    logger.info(string_results)
    logger.info("All contracts are valid")


@contract.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="check",
    epilog="""Example:

        gable contract check --contract-id id --source-type postgres --user root --password MyPassword --host localhost --db myDataBase --schema public --table my_table""",
)
@click.pass_context
@click.option("--contract-id", required=True, type=str)
@click.option("--source-type", required=True, type=str)
@click.option("--user", type=str, default=None)
@click.option("--password", type=str, hide_input=True, default=None)
@click.option("--db", type=str, default=None)
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=5432)
@click.option("--schema", type=str, default="public")
@click.option("--table", type=str)
@click.option("--file", type=click.File(), default=None)
@global_options()
def check_data_asset(
    ctx: ClickContext,
    contract_id: str,
    source_type: str,
    user: str,
    password: str,
    db: str,
    host: str,
    port: int,
    schema: str,
    table: str,
    file: click.File,
) -> None:
    """Checks if a data asset is compliant with a contract"""
    schema_contents = get_schema_contents(
        source_type=source_type,
        dbuser=user,
        dbpassword=password,
        db=db,
        dbhost=host,
        dbport=port,
        schema=schema,
        tables=[table],
        files=[file.name] if file else [],
    )

    response, success = post_contract_check_request(
        client=ctx.obj.client,
        contract_id=contract_id,
        source_type=source_type,
        schema_contents=schema_contents[0],  # type: ignore
    )
    if not success:
        raise click.ClickException(f"Check failed: {response}")
    logger.info(f"\u2705 {response}")

# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import click
import yaml

from dyff.api.backend.base.auth import AuthBackend
from dyff.api.tokens import (
    ACCOUNT_TOKEN,
    TOKEN_CHOICES,
    Signer,
    generate_api_key,
    get_signer,
    hashed_api_key,
)
from dyff.core import dynamic_import
from dyff.core.config import config
from dyff.schema.platform import AccessGrant, Entities

from . import roles


@click.group()
def tokens():
    pass


def get_comma_separated_list(ctx, _param, value) -> list[str]:
    if value is None:
        return []
    values = value.split(",")
    return values


@tokens.command()
@click.option(
    "token_type",
    "--type",
    "-t",
    type=click.Choice(TOKEN_CHOICES),
    required=True,
    help="Type of API key to create.",
)
@click.option(
    "account_id",
    "--account-id",
    "-i",
    metavar="ID",
    type=str,
    help="Account ID to associate token with.",
)
@click.option(
    "resources",
    "--resources",
    "-r",
    type=str,
    callback=get_comma_separated_list,
    help="Resources to grant access to.",
)
@click.option(
    "functions",
    "--functions",
    "-f",
    type=str,
    callback=get_comma_separated_list,
    help="Functions to grant access to.",
)
@click.option(
    "accounts",
    "--accounts",
    "-a",
    type=str,
    callback=get_comma_separated_list,
    help="Accounts to grant access to.",
)
@click.option(
    "entities",
    "--entities",
    "-e",
    type=str,
    callback=get_comma_separated_list,
    help="Entities to grant access to.",
)
@click.option(
    "config_file",
    "--config",
    "-c",
    type=click.File(),
    help="Access grant config file specified with JSON / YAML.",
)
@click.option("role", "--role", type=str, help="Named Role specifying access grants")
def create(
    role: str,
    config_file: str,
    account_id: str,
    token_type: str,
    resources: list[str],
    functions: list[str],
    accounts: list[str],
    entities: list[str],
):
    auth_backend: AuthBackend = dynamic_import.instantiate(config.api.auth.backend)

    if token_type != ACCOUNT_TOKEN:
        raise NotImplementedError("ephemeral token support has not yet been added.")

    if role and config_file:
        raise click.ClickException("--role and --config are mutually exclusive")

    if role:
        spec = roles.named_role(role, account_id)
        account_id = spec["account"]
        grants = spec["grants"]
    elif config_file:
        spec = yaml.safe_load(config_file)
        account_id = spec["account"]
        grants = [AccessGrant.parse_obj(grant) for grant in spec["grants"]]
    else:
        if account_id is None:
            raise click.UsageError("--account-id/-a must be specified")
        grants = [
            AccessGrant.parse_obj(
                dict(
                    accounts=accounts,
                    entities=entities,
                    functions=functions,
                    resources=resources,
                )
            )
        ]

    auth_backend.get_account(id=account_id)

    signer: Signer = get_signer(
        config.api.auth.api_key_signing_secret.get_secret_value()
    )
    api_key = generate_api_key(
        subject_type=Entities.Account,
        subject_id=account_id,
        grants=grants,
        generate_secret=True,
    )
    hashed_key = hashed_api_key(api_key)
    signed_key = signer.sign_api_key(api_key)

    auth_backend.revoke_all_api_keys(account_id)
    auth_backend.add_api_key(account_id, hashed_key)
    click.echo(signed_key)

# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import click

from dyff.api.backend.base.auth import AuthBackend
from dyff.api.exceptions import EntityExistsError, EntityNotFoundError
from dyff.core import dynamic_import
from dyff.core.config import config


@click.group()
def accounts():
    pass


@accounts.command()
@click.option(
    "account_name", "--name", "-n", metavar="NAME", required=True, help="Account name"
)
def create(account_name: str):
    auth_backend: AuthBackend = dynamic_import.instantiate(config.api.auth.backend)
    try:
        account = auth_backend.create_account(account_name)
        click.echo(f"created account: '{account.name}' ({account.id})", err=True)
    except EntityExistsError as excinfo:
        raise click.ClickException(" ".join(excinfo.args))


@accounts.command()
@click.option(
    "account_name",
    "--name",
    "-n",
    metavar="NAME",
    type=str,
    default=None,
    help="Account name",
)
@click.option(
    "account_id", "--id", "-i", metavar="ID", type=str, default=None, help="Account ID"
)
def get(account_id: Optional[str], account_name: Optional[str]):
    if not (bool(account_id) ^ bool(account_name)):
        raise click.ClickException("Must specify exactly one of {--name, --id}")
    auth_backend: AuthBackend = dynamic_import.instantiate(config.api.auth.backend)
    try:
        account = auth_backend.get_account(id=account_id, name=account_name)
        if account is not None:
            click.echo(account.json(indent=2))
    except Exception as ex:
        raise click.ClickException(" ".join(ex.args)) from ex


@accounts.command()
@click.option(
    "account_id", "--id", "-i", metavar="ID", required=True, help="Account ID"
)
def delete(account_id: str):
    auth_backend: AuthBackend = dynamic_import.instantiate(config.api.auth.backend)
    try:
        auth_backend.delete_account(account_id)
        click.echo(f"deleted account: {account_id}", err=True)
    except NotImplementedError:
        raise click.ClickException(
            "Account deletion is not implemented for this auth backend"
        )
    except EntityNotFoundError as excinfo:
        raise click.ClickException(" ".join(excinfo.args))

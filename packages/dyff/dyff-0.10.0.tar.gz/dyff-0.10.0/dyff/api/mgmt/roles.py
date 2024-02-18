# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json

import click
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from dyff.schema.platform import AccessGrant, APIFunctions, Resources


def admin(account_id: str) -> dict:
    grants = [
        AccessGrant(
            resources=[Resources.ALL],
            functions=[APIFunctions.all],
            accounts=["*"],
            entities=["*"],
        ),
    ]
    return {
        "account": account_id,
        "grants": grants,
    }


def audit_developer(account_id: str) -> dict:
    grants = [
        AccessGrant(
            resources=[Resources.ALL],
            functions=[APIFunctions.get, APIFunctions.query],
            accounts=["*"],
            entities=["*"],
        ),
        AccessGrant(
            resources=[Resources.ALL],
            functions=[APIFunctions.consume, APIFunctions.data],
            accounts=["public"],
        ),
        AccessGrant(
            resources=[Resources.ALL],
            functions=[APIFunctions.all],
            accounts=[account_id],
        ),
    ]
    return {
        "account": account_id,
        "grants": grants,
    }


def named_role(role_name: str, account_id: str) -> dict:
    if role_name == "Admin":
        return admin(account_id)
    elif role_name == "AuditDeveloper":
        return audit_developer(account_id)
    else:
        raise ValueError(f"Unknown role: {role_name}")


@click.group()
def roles():
    pass


@roles.command()
@click.argument("role", type=str, metavar="ROLE", required=True)
@click.option(
    "account_id", "--id", "-i", type=str, metavar="ID", required=True, help="Account ID"
)
def get(role: str, account_id: str):
    try:
        config = named_role(role, account_id)
        # Easy way to convert enum members to strings
        config["grants"] = [json.loads(grant.json()) for grant in config["grants"]]
        s = StringIO()
        YAML().dump(config, s)
        click.echo(s.getvalue())
    except Exception as ex:
        raise click.ClickException(" ".join(ex.args)) from ex

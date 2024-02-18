# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib
from pathlib import Path

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Management interface for dyff.api."""


def get_command_from_path(command_path):
    command_name = command_path.stem
    package_name = ".".join(__loader__.name.split(".")[:-1])
    module = importlib.import_module(f".{command_name}", package=package_name)
    return getattr(module, command_name)


command_paths = Path(__file__).parent.glob("*.py")
for command_path in command_paths:
    if command_path.name.startswith("_"):
        continue
    main.add_command(get_command_from_path(command_path))


if __name__ == "__main__":
    main()

# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib.resources
import os
import pathlib
import string
import subprocess

import ruamel.yaml as yaml

from dyff.schema.platform import ModelSourceOpenLLM


def fetch(local_path: str, spec: ModelSourceOpenLLM):
    cmd = [
        "openllm",
        "build",
        spec.modelKind,
        "--model-id",
        spec.modelID,
        "--model-version",
        spec.modelVersion,
    ]
    env = os.environ.copy()
    env.update({"BENTOML_HOME": local_path})
    print(f"command: {cmd}")
    print(f"env: {env}")
    subprocess.run(cmd, env=env, check=True)

    # Subdirectory of BENTOML_HOME that holds the Bento service package
    bentoml_service_name = f"{spec.modelID.replace('/', '--')}-service"
    service_dir = (
        pathlib.Path(local_path) / "bentos" / bentoml_service_name / spec.modelVersion
    )

    # Create our own bentoml.Service definition because the generated one
    # sometimes introduces extra endpoints for which we don't want to
    # provide the dependencies (i.e., /v1/embeddings)
    service_template = importlib.resources.read_text(
        "dyff.models.bentoml", "template_openllm_service.py"
    )
    service_definition = string.Template(service_template).substitute(
        {"openllm_base_model": spec.modelKind}
    )
    with open(service_dir / "src" / "openllm_service.py", "w") as service_file:
        service_file.write(service_definition)
    # TODO: Generate the OpenAPI spec for our modified service

    # Modify the bentofile to use our service definition
    with open(service_dir / "bento.yaml", "r") as bentofile_in:
        bentofile = yaml.safe_load(bentofile_in)
    bentofile["service"] = "openllm_service:svc"
    with open(service_dir / "bento.yaml", "w") as bentofile_out:
        yaml.safe_dump(bentofile, bentofile_out)
    # TODO: There's some extra stuff in the bentofile that does not apply
    # to our modified service (such as the llm-generic-embedding runner).
    # It would be good to remove the extra stuff.

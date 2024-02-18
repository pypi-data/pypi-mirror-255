# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import subprocess
import tarfile
from pathlib import Path

import absl.app
import absl.flags
import requests
import ruamel.yaml
from absl import logging
from ruamel.yaml.compat import StringIO as YAMLStringIO

from ...client import Client
from ...schema.platform import Audit
from ..sanitize import sanitize_relative_file_path

# ----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "audit_yaml", None, "Path to a YAML file containing the Audit manifest."
)
absl.flags.DEFINE_string(
    "jupyterbook_path", None, "Path to root directory of jupyter book source code."
)
absl.flags.mark_flags_as_required(["audit_yaml", "jupyterbook_path"])

absl.flags.DEFINE_integer(
    "proxy_port",
    8080,
    "Send a request to http://localhost:{proxy_port}/terminate as the last step of execution.",
)

# ----------------------------------------------------------------------------


def main(_unused_argv):
    logging.set_verbosity(logging.INFO)

    dyff = Client()

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.audit_yaml, "r") as fin:
        audit_yaml = yaml.load(fin)
    yaml_string = YAMLStringIO()
    yaml.dump(audit_yaml, yaml_string)
    logging.info(f"audit_yaml:\n{yaml_string.getvalue()}")

    audit = Audit.parse_obj(audit_yaml["spec"])
    jupyterbook_path = Path(FLAGS.jupyterbook_path)

    # Extract the .tar.gz archive
    data = dyff.auditprocedures.download(audit.auditProcedure)
    with tarfile.open(fileobj=data, mode="r:gz") as tgz:
        for member in tgz:
            path = sanitize_relative_file_path(member.name)
            member_file = tgz.extractfile(str(path))
            with open(jupyterbook_path / path, "wb") as fout:
                fout.write(member_file.read())

    # Note: These next two steps shouldn't be necessary if the jupyterbook
    # source was validated on ingestion, but these are untrusted inputs so we'll
    # program defensively.

    # Clear notebook output
    for nb in jupyterbook_path.rglob("*.ipynb"):
        logging.info(f"clearing output in notebook {nb}")
        subprocess.run(
            ["jupyter", "nbconvert", "--clear-output", "--inplace", str(nb)], check=True
        )

    # Overwrite _config.yml with mandatory settings
    with open(jupyterbook_path / "_config.yml", "r") as fin:
        jb_config = yaml.load(fin)
    execute = jb_config.get("execute", {})
    execute["execute_notebooks"] = "force"
    execute["timeout"] = -1  # No limit (timeout should be imposed by k8s Job)
    jb_config["execute"] = execute
    with open(jupyterbook_path / "_config.yml", "w") as fout:
        yaml.dump(jb_config, fout)

    # Run the audit
    subprocess.run(["jupyter-book", "build", FLAGS.jupyterbook_path], check=True)

    # Construct a .tar.gz archive of the HTML output and upload it
    output_root = Path(FLAGS.jupyterbook_path) / "_build" / "html"
    files = (f for f in output_root.rglob("*") if f.is_file())
    # TODO: replace() currently needed because old-style IDs look like 'account/entity'
    # Can be removed after schema migration.
    archive_path = output_root / f"audit-{audit.id.replace('/', '-')}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tgz:
        for f in files:
            logging.info(f"copying {f}")
            relative_path = f.relative_to(output_root)
            with open(f, "rb") as fin:
                tarinfo = tgz.gettarinfo(arcname=relative_path, fileobj=fin)
                tgz.addfile(tarinfo, fin)
    dyff.audits.upload(key=audit.id, file_path=str(archive_path))

    # Explicitly terminate the sidecar proxy
    try:
        requests.post(f"http://localhost:{FLAGS.proxy_port}/terminate")
    except:
        pass


if __name__ == "__main__":
    absl.app.run(main)

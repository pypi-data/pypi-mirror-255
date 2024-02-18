# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os

import absl.app
import absl.flags
import nbconvert
import nbformat
import ruamel.yaml
import smart_open
from absl import logging
from ruamel.yaml.compat import StringIO as YAMLStringIO

from dyff.api import storage

# -----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "audit_yaml", None, "Path to a YAML file containing the Audit manifest."
)
absl.flags.mark_flag_as_required("audit_yaml")

# -----------------------------------------------------------------------------


def main(_unused_argv):
    logging.set_verbosity(logging.INFO)

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.audit_yaml, "r") as fin:
        audit_yaml = yaml.load(fin)
    yaml_string = YAMLStringIO()
    yaml.dump(audit_yaml, yaml_string)
    logging.info(f"audit_yaml:\n{yaml_string.getvalue()}")

    audit_id = audit_yaml["metadata"]["labels"]["audit"]
    auditprocedure_id = audit_yaml["spec"]["auditProcedure"]
    inferenceservice_id = audit_yaml["spec"]["inferenceService"]
    os.environ["ALIGNMENTLABS_AUDIT_SYSTEM_UNDER_TEST"] = inferenceservice_id

    with smart_open.open(
        storage.paths.auditprocedure_notebook(auditprocedure_id), "r"
    ) as fin:
        nb = nbformat.read(fin, as_version=4)

    execute_preprocessor = nbconvert.preprocessors.ExecutePreprocessor()
    execute_body, execute_resources = execute_preprocessor.preprocess(nb)

    html_exporter = nbconvert.HTMLExporter(exclude_input=True)
    html_body, resources = html_exporter.from_notebook_node(execute_body)

    with smart_open.open(storage.paths.auditreport_html(audit_id), "w") as fout:
        fout.writelines(html_body)


if __name__ == "__main__":
    absl.app.run(main)

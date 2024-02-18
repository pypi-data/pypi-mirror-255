# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from ...core.config import config


def auditprocedure_notebook(auditprocedure_id: str) -> str:
    return f"{config.resources.auditprocedures.storage.url}/{auditprocedure_id}/notebook.ipynb"


def auditreport_html(audit_id: str) -> str:
    return f"{auditreport_root(audit_id)}/index.html"


def auditreport_root(audit_id: str) -> str:
    return f"{config.resources.auditreports.storage.url}/{audit_id}"


def dataset_root(dataset_id: str) -> str:
    return f"{config.resources.datasets.storage.url}/{dataset_id}"


def dataset_data(dataset_id: str) -> str:
    return f"{dataset_root(dataset_id)}/data"


def dataset_strata(dataset_id: str) -> str:
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return f"{dataset_root(dataset_id)}/strata/part-0.parquet"


def dataset_task(dataset_id: str, task_id: str) -> str:
    return f"{config.resources.datasets.storage.url}/{dataset_id}/tasks/{task_id}"


def datasource_root(datasource_id: str) -> str:
    return f"{config.resources.datasources.storage.url}/{datasource_id}"


def outputs_raw(evaluation_id: str) -> str:
    return f"{config.resources.outputs.storage.url}/{evaluation_id}/data"


def outputs_verified(evaluation_id: str) -> str:
    return f"{config.resources.outputs.storage.url}/{evaluation_id}/verified"


def report_data(report_id: str) -> str:
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return f"{report_root(report_id)}/part-0.parquet"


def report_root(report_id: str) -> str:
    return f"{config.resources.reports.storage.url}/{report_id}"


def inferenceservice_source_archive(inferenceservice_id: str) -> str:
    return f"{config.resources.inferenceservices.storage.url}/{inferenceservice_id}/source.tar.gz"


def model_source_archive(model_id: str) -> str:
    return f"{config.resources.models.storage.url}/{model_id}/source.tar.gz"

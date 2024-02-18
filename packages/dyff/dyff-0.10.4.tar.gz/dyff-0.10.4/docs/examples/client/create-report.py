# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.client import Client
from dyff.schema.requests import ReportCreateRequest

API_KEY: str = ...
ACCOUNT: str = ...

dyffapi = Client(api_key=API_KEY)

report_request = ReportCreateRequest(
    account=ACCOUNT,
    rubric="example.LikeCount",
    evaluation="825e3b76d74a446e997a8ea9c78b2d42",
)

report = dyffapi.reports.create(report_request)
print(f"created report:\n{report}")

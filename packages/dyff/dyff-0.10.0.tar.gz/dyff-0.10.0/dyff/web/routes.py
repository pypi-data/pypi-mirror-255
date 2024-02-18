# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os

import fastapi
import jinja2
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from dyff.client import Client

DYFF_API_KEY = os.environ.get("DYFF_API_KEY")
dyff_api = Client(api_key=DYFF_API_KEY)


def _generate_unique_id(route: fastapi.routing.APIRoute) -> str:
    """Strip everything but the function name from the ``operationId`` fields."""
    return route.name


def check_route_permissions(request: fastapi.Request) -> None:
    pass


jenv = jinja2.Environment(
    loader=jinja2.PackageLoader("dyff.web"), autoescape=jinja2.select_autoescape()
)


app = fastapi.FastAPI(
    title="Dyff Cloud Console",
    generate_unique_id_function=_generate_unique_id,
    dependencies=[fastapi.Depends(check_route_permissions)],
)


this_dir = os.path.dirname(__file__)
static_dir = os.path.join(this_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def homepage() -> HTMLResponse:
    template = jenv.get_template("home.jinja")
    return HTMLResponse(template.render())


@app.get("/models/")
def models() -> HTMLResponse:
    template = jenv.get_template("models.jinja")
    return HTMLResponse(template.render())


@app.get("/models/data")
def models_all(model_id: str = None, account: str = "public") -> HTMLResponse:
    id = model_id if model_id != "" else None
    acc = account if account != "" else None
    models = dyff_api.models.query(id=id, account=acc)

    # Loop and generate random status to test dynamic status

    # Extract data in here for typing - no typing in .jinja
    headers = ["id", "name", "account", "source", "creationTime", "status"]
    body = [
        [m.id, m.name, m.account, m.source.kind, m.creationTime, m.status]
        for m in models
    ]

    template = jenv.get_template("table.jinja")
    return HTMLResponse(template.render(headers=headers, body=body, label="Models"))


@app.get("/reports/")
def reports() -> HTMLResponse:
    template = jenv.get_template("reports.jinja")
    return HTMLResponse(template.render())


@app.get("/reports/data")
def reports_all(report_id: str = None, account: str = None) -> HTMLResponse:
    id = report_id if report_id != "" else None
    acc = account if account != "" else None
    reports = dyff_api.reports.query(account=acc, id=id)

    # Extract data in here for typing - no typing in .jinja
    headers = ["id", "account", "evaluation", "creationTime", "status"]
    body = [[r.id, r.account, r.evaluation, r.creationTime, r.status] for r in reports]

    template = jenv.get_template("table.jinja")
    return HTMLResponse(template.render(headers=headers, body=body, label="Reports"))

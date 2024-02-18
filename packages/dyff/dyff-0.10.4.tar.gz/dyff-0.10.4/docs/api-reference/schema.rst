:mod:`dyff.schema` --- Data Model
=================================

The Dyff Platform uses `pydantic models <https://docs.pydantic.dev/1.10/>`_ to
formalize all of its data schemas. Pydantic models can be converted easily to
and from JSON objects, and they perform validation when loading JSON data. We
also use the models to generate schemas in the JSON Schema format, which, in
turn, form part of the OpenAPI specification of the Dyff Platform API.

Note that we currently use pydantic v1.10, as pydantic v2 is
backwards-incompatible.

To convert a model to a JSON object, use ``model.dict()``; to create a model
from a JSON object, use ``ModelType.parse_obj()``. Note that in some cases, the
"canonical name" of a field is not valid as a pydantic model field name, either
because it conflicts with fields inherited from ``pydantic.BaseModel``, or
because it is a Python reserved word like ``bytes``. In these cases, the field
will have an ``alias`` set to its canonical name. All Dyff Platform schemas
derive from :class:`DyffSchemaBaseModel
<dyff.schema.pydantic.DyffSchemaBaseModel>`, which overrides ``dict()`` and
``json()`` so that they default to using the aliases as the keys when building
JSON objects. You generally should *not* override this behavior.

Core Platform Types
-------------------

The core platform types are the ones that you create, manage, and query through
the Dyff API. The core types describe the steps of the auditing workflow that
produces audit reports from models and data. Instances of core types all have a
unique ``.id``, belong to an ``.account``, and have additional metadata fields
that are updated by the platform. In particular, the ``.status`` and ``.reason``
fields tell you how the work is proceeding and whether it is complete or
encountered an error.

.. autopydantic_model:: dyff.schema.platform.Audit
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.AuditProcedure
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.Dataset
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.DataSource
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.Evaluation
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.Model
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.InferenceService
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.InferenceSession
   :inherited-members: DyffSchemaBaseModel

.. autopydantic_model:: dyff.schema.platform.Report
   :inherited-members: DyffSchemaBaseModel

.. .. autopydantic_model:: dyff.schema.platform.Task
..    :inherited-members: DyffSchemaBaseModel

Request Types
-------------

.. automodule:: dyff.schema.requests
   :members:
   :inherited-members: DyffSchemaBaseModel

Additional Platform Types
-------------------------

.. automodule:: dyff.schema.platform
   :members:
   :exclude-members: Audit, AuditProcedure, Dataset, DataSource, Evaluation, Model, InferenceService, InferenceSession, Report, Task
   :inherited-members: DyffSchemaBaseModel

Status Flags
------------

.. autodata:: dyff.schema.platform.JobStatus

.. autodata:: dyff.schema.platform.EntityStatus

.. autodata:: dyff.schema.platform.EntityStatusReason

.. autodata:: dyff.schema.platform.AuditStatus

.. autodata:: dyff.schema.platform.DataSourceStatus

.. autodata:: dyff.schema.platform.DatasetStatus

.. autodata:: dyff.schema.platform.DatasetStatusReason

.. autodata:: dyff.schema.platform.EvaluationStatus

.. autodata:: dyff.schema.platform.EvaluationStatusReason

.. autodata:: dyff.schema.platform.InferenceServiceStatus

.. autodata:: dyff.schema.platform.InferenceServiceStatusReason

.. autodata:: dyff.schema.platform.ModelStatus

.. autodata:: dyff.schema.platform.ModelStatusReason

.. autodata:: dyff.schema.platform.ReportStatus

.. autodata:: dyff.schema.platform.ReportStatusReason

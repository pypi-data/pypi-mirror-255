#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json
import sys

# If we specify documentation with pydantic.Field(description=...) for a
# non-primitive attribute, then fastapi will put the
# ``"$ref": "#/components/schema/..."`` bit inside a superfluous ``"allOf"``.
#
# For a nested enum:
#
#   "sourceKind": {
#     "description": "The kind of source from which the InferenceService is obtained.",
#     "allOf": [
#       {
#         "$ref": "#/components/schemas/InferenceServiceSources"
#       },
#     ]
#
# Or, for a nested object:
#
#   "modelConfiguration": {
#     "title": "Modelconfiguration",
#     "description": "How to configure the Model for the Evaluation (e.g., hyperparameters).",
#     "allOf": [
#       {
#         "$ref": "#/components/schemas/ModelConfiguration"
#       }
#     ]
#   },
#
# This will then break autorest, with a message like:
#
#   warning | PreCheck/SchemaMissingType | The schema 'Evaluation-modelConfiguration' with an undefined type and 'allOf'/'anyOf'/'oneOf' is a bit ambiguous. This has been auto-corrected to 'type:object'
#
# Followed by an error like this:
#
#   error   | PreCheck/AllOfTypeDifferent | Schema 'InferenceService-sourceKind' has an allOf reference to 'InferenceServiceSources' but those schema have different types:
#     - InferenceService-sourceKind: object
#     - InferenceServiceSources: string
#
# This script removes the problematic ``"allOf"``s
#
# It is very fragile and may not work if the structure of the models changes
# significantly.
#
# TODO: File a bug report with pydantic and/or fastapi
# The problematic function is pydantic.schema.get_schema_ref(), which adds
# the "allOf" wrapper because the ``schema_overrides`` flag is ``True``. This,
# in turn, is because pydantic.schema.get_field_info_schema() sets that
# flag to ``True`` because we manually specified ``description``.


def main(argv):
    file_path = argv[1]
    with open(file_path, "r") as fin:
        openapi = json.load(fin)

    # Remove the 'allOf' wrappers
    for schema_name, schema_spec in openapi["components"]["schemas"].items():
        if "properties" in schema_spec:
            for name, spec in schema_spec["properties"].items():
                if "allOf" in spec:
                    ref = spec["allOf"][0]["$ref"]
                    del spec["allOf"]
                    spec["$ref"] = ref

    # Remove patternProperties, which is part of JSON Schema but not supported
    # in OpenAPI 3.0
    entities_with_pattern_properties = [
        "Audit",
        "Dataset",
        "Evaluation",
        "InferenceService",
        "InferenceSession",
        "LabelUpdateRequest",
        "Model",
        "Report",
    ]
    for schema_name, schema_spec in openapi["components"]["schemas"].items():
        if schema_name in entities_with_pattern_properties:
            try:
                labels = schema_spec["properties"]["labels"]
                del labels["patternProperties"]
            except:
                pass

            try:
                annotations = schema_spec["properties"]["annotations"]
                del annotations["patternProperties"]
            except:
                pass

    with open(file_path, "w") as fout:
        json.dump(openapi, fout, indent=2)


if __name__ == "__main__":
    main(sys.argv)

# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib
from collections import defaultdict

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective


def symbol(fully_qualified_name):
    tokens = fully_qualified_name.split(".")
    module_name = ".".join(tokens[:-1])
    member = tokens[-1]
    module = importlib.import_module(module_name)
    return getattr(module, member)


def instantiate(fully_qualified_name, *args, **kwargs):
    constructor = symbol(fully_qualified_name)
    return constructor(*args, **kwargs)


def _True(x):
    return x


class PyArrowSchema(SphinxDirective):
    required_arguments = 1
    optional_arguments = 10
    option_spec = defaultdict(lambda: directives.unchanged)
    has_content = False

    def run(self):
        data_type = instantiate(*self.arguments)
        items = []
        for i, field in enumerate(data_type.schema):
            print(field)
            doc = self.options.get(field.name, "")
            items.append(
                nodes.definition_list_item(
                    "",
                    nodes.term(text=field.name),
                    nodes.classifier(text=str(field.type)),
                    nodes.definition("", nodes.paragraph("", doc)),
                )
            )
            items[-1].line = i

        root = nodes.definition_list("", *items)
        print(root.pformat(indent="  "))
        return [root]


def setup(app):
    app.add_directive("pyarrow-schema", PyArrowSchema)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

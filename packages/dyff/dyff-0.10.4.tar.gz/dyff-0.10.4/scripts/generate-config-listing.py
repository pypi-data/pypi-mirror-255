#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import sys
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from dyff.core.config import DyffConfig

SCHEMA = DyffConfig.schema()

ENV_PREFIX = DyffConfig.Config.env_prefix
ENV_FILE = DyffConfig.Config.env_file
ENV_NESTED_DELIMITER = DyffConfig.Config.env_nested_delimiter


def title_case_to_snake_case(text: str) -> str:
    return text.replace(" ", "_").lower()


def snake_case_to_camel_case(text: str) -> str:
    if "_" in text:
        segments = text.split("_")
        return segments[0] + "".join(segment.title() for segment in segments[1:])
    return text


@dataclass(frozen=True)
class PropertyDoc:
    sections: Tuple[str]
    name: str
    full_name: str
    environment_variable: str
    helm_chart_value: str
    type: str
    sensitive: bool = False
    default: Any = None
    examples: List[str] = field(default_factory=list)
    description: str = ""


def get_default_field(property_data: dict) -> Optional[str]:
    return property_data["default"] if "default" in property_data else None


def get_description_field(property_data: dict) -> str:
    return property_data["description"] if "description" in property_data else ""


def get_examples_field(property_data: dict) -> List[str]:
    if "examples" not in property_data:
        return []
    return property_data["examples"]


def get_sensitive_field(property_data: dict) -> bool:
    return (
        property_data["writeOnly"]
        if ("writeOnly" in property_data and property_data["writeOnly"])
        else False
    )


def get_property_doc(
    property_data: dict, sections: Optional[List[str]] = None
) -> PropertyDoc:
    name = title_case_to_snake_case(property_data["title"])
    full_name = ENV_NESTED_DELIMITER.join([*sections[1:], name])
    environment_variable = f"{ENV_PREFIX}{full_name}".upper()

    parts = full_name.replace(ENV_NESTED_DELIMITER, ".").split(".")
    helm_chart_parts = []
    for part in parts:
        helm_chart_parts.append(snake_case_to_camel_case(part))
    helm_chart_value = ".".join(helm_chart_parts)

    return PropertyDoc(
        name=name,
        full_name=full_name,
        environment_variable=environment_variable,
        helm_chart_value=helm_chart_value,
        sections=tuple(sections[1:]),
        sensitive=get_sensitive_field(property_data),
        type=property_data["type"],
        default=get_default_field(property_data),
        examples=get_examples_field(property_data),
        description=get_description_field(property_data),
    )


def get_property_doc_list(
    root_name: str, root_definition: dict, sections=None
) -> List[PropertyDoc]:
    _properties = []

    _sections = []
    if sections is not None:
        _sections.extend(sections)
    _sections.append(title_case_to_snake_case(root_name))

    for propname, prop in root_definition["properties"].items():
        if "type" in prop:
            _properties.append(get_property_doc(property_data=prop, sections=_sections))
        else:
            if "allOf" in prop:
                ref = prop["allOf"][0]["$ref"]
            else:
                ref = prop["$ref"]
            definition = ref.split("/")[-1]
            _properties.extend(
                get_property_doc_list(
                    propname, SCHEMA["definitions"][definition], sections=_sections
                )
            )
    return _properties


def render_heading(text: str, level: int = 0) -> str:
    char: str = {
        0: "=",
        1: "-",
        2: "~",
        3: "`",
        4: "'",
    }[level]
    return f"{text}\n" f"{char * len(text)}"


def render_section_heading(
    sections: Tuple[str], previous: Optional[Tuple[str]] = None
) -> List[str]:
    if previous is None:
        previous = tuple()

    # do nothing if fully matching
    if previous == sections:
        return []

    min_sections = min(len(previous), len(sections))

    index = 0
    while index < min_sections:
        if previous[index] != sections[index]:
            break
        index += 1

    headings = []
    for level in range(len(sections)):
        if previous[: level + 1] == sections[: level + 1]:
            continue
        headings.append(
            render_heading(text=".".join(sections[: level + 1]), level=level + 1)
        )
    return headings


def render_property_heading(sections: Tuple[str]) -> List[str]:
    text = ".".join(sections)
    return render_heading(text=text, level=len(sections))


def render_sphinx_output(property_docs: List[PropertyDoc]) -> str:
    rendered = []
    current_sections = None

    rendered.append(render_heading("Configuration"))

    for property_doc in property_docs:
        previous_sections = current_sections

        if property_doc.sections:
            if current_sections and current_sections != property_doc.sections:
                current_sections = property_doc.sections
                rendered.extend(
                    render_section_heading(current_sections, previous=previous_sections)
                )
            elif not current_sections:
                current_sections = property_doc.sections
                rendered.extend(
                    render_section_heading(current_sections, previous=previous_sections)
                )

        elif not current_sections:
            current_sections = tuple()
            rendered.extend(
                render_section_heading(current_sections, previous=previous_sections)
            )

        property_section = tuple(list(current_sections) + [property_doc.name])
        rendered.append(render_property_heading(property_section))

        if property_doc.sensitive:
            rendered.extend(
                [
                    f".. warning::",
                    "     **This value is secret** and should not be shared.",
                ]
            )

        if property_doc.type:
            rendered.append(f"Type: ``{property_doc.type}``")

        if property_doc.default:
            rendered.append(f"Default: ``{property_doc.default}``")

        rendered.append(
            f"Environment variable: ``{property_doc.environment_variable}``"
        )

        if property_doc.description:
            rendered.append(f"{property_doc.description}")

        if property_doc.examples:
            rendered.extend(
                [
                    f".. tabs::",
                    f"    .. group-tab:: Environment variable",
                ]
            )
            for example in property_doc.examples:
                rendered.extend(
                    [
                        f"        .. code-block:: bash",
                        (
                            (
                                "            # do not use the value listed here\n"
                                if property_doc.sensitive
                                else ""
                            )
                            + f'            {property_doc.environment_variable}="{example}"'
                        ),
                    ]
                )
    return "\n\n".join(rendered) + "\n"


def main():
    property_docs = sorted(
        get_property_doc_list("dyff", SCHEMA), key=lambda p: (p.sections, p.name)
    )
    output = render_sphinx_output(property_docs=property_docs)
    sys.stdout.write(output)


if __name__ == "__main__":
    main()

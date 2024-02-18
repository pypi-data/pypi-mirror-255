# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("_extensions"))

project = "Dyff"
copyright = "2023 UL Research Institutes"
author = "Digital Safety Research Institute at UL Research Institutes"

extensions = [
    "autoapi.extension",
    "nbsphinx",
    "pyarrow_schema",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.graphviz",
    "sphinx_click",
    "sphinx_copybutton",
    "sphinx_sitemap",
    "sphinx_toolbox.code",
    "sphinx_tabs.tabs",
    "sphinxcontrib.autodoc_pydantic",
    "sphinxext.opengraph",
]

highlight_language = "none"

# autodoc_typehints = "both"

autoapi_type = "python"
autoapi_generate_api_docs = False
autoapi_python_use_implicit_namespaces = True
autoapi_dirs = ["../dyff"]
autoapi_add_toctree_entry = True

autoapi_options = [
    "members",
    "inherited-members",
    "undoc-members",
    "special-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

add_module_names = False
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "show-module-summary": True,
    "imported-members": True,
}
autodoc_member_order = "groupwise"

# Note: 'bygroup' doesn't work for summary_list_order; you will get an error to the effect of:
# TypeError: can't compare NoneType and NoneType using '<'
autodoc_pydantic_model_summary_list_order = "alphabetical"
autodoc_pydantic_model_member_order = "groupwise"

autosummary_generate = True
# autosummary_imported_members = True

# templates_path = ['_templates']

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

copybutton_exclude = ".linenos, .gp"
graphviz_output_format = "svg"

# -- Options for HTML output -------------------------------------------------

html_baseurl = "https://docs.dyff.io/"

html_title = "Dyff docs"
html_theme = "furo"

# html_static_path = ['_static']

html_theme_options = {
    # TODO: work with designer on colors
    # https://github.com/pradyunsg/furo/blob/main/src/furo/assets/styles/variables/_colors.scss
    # "dark_css_variables": {
    #     "color-foreground-primary": "#FFFF00",
    #     "color-brand-primary": "#FF0000",
    #     "color-brand-content": "#00FF00",
    # },
    # "light_css_variables": {
    #     "color-foreground-primary": "#00FFFF",
    #     "color-brand-primary": "#0000FF",
    #     "color-brand-content": "#FF00FF",
    # },
    # TODO: uncomment when public
    # "source_repository": "https://gitlab.com/dyff/dyff/",
    # "source_branch": "main",
    # "source_directory": "docs/",
}


sphinx_tabs_disable_tab_closing = True

# sphinx_tabs_disable_css_loading = True

ogp_site_url = "https://docs.dyff.io/"

sitemap_url_scheme = "{link}"

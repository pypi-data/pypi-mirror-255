#: ===================
#: Project Information
#: ===================

# The documented project's name:
project: str = "jsonrpc-py"

#: =====================
#: General Configuration
#: =====================

# A list of strings that are module names of extensions:
extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

# Highlighting of the code blocks:
pygments_style: str = "stata-light"

# This variable is Furo-specific at this time:
pygments_dark_style: str = "stata-dark"

#: =======================
#: Options for HTML Output
#: =======================

# The "theme" that the HTML output should use:
html_theme: str = "furo"

# The "title" for HTML documentation:
html_title: str = project

# The base URL which points to the root of the HTML documentation:
html_baseurl: str = "https://docs.jsonrpc.ru"

# If true, the reST sources are included in the HTML build as _sources/name:
html_copy_source: bool = False

# If true, "© Copyright ..." is shown in the HTML footer:
html_show_copyright: bool = False

# Automatically documented members are sorted by source order:
autodoc_member_order: str = "bysource"

# Don't show typehints in docstrings:
autodoc_typehints: str = "none"

# The locations and names of other projects
# that should be linked to in this documentation:
intersphinx_mapping: dict[str, tuple[str, None]] = {
    "python": ("https://docs.python.org/3.11/", None),
}

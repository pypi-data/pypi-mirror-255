#!/usr/bin/env python3
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

#
# JupyterLab documentation build configuration file, created by
# sphinx-quickstart on Thu Jan  4 15:10:23 2018.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import json
import os
import shutil
import time
from collections import ChainMap
from functools import partial
from pathlib import Path
from subprocess import check_call
from typing import List

HERE = Path(__file__).parent.resolve()

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
]

myst_enable_extensions = ["html_image"]
myst_heading_anchors = 3

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The file extensions of source files.
# Sphinx considers the files with this suffix as sources.
# The value can be a dictionary mapping file extensions to file types.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "JupyterLab"
copyright = f"2018-{time.localtime().tm_year}, Project Jupyter"  # noqa
author = "Project Jupyter"


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

_version_py = HERE.parent.parent / "jupyterlab" / "_version.py"
version_ns = {}

exec(_version_py.read_text(), version_ns)  # noqa

# The short X.Y version.
version = "{0:d}.{1:d}".format(*version_ns["version_info"])  # noqa
# The full version, including alpha/beta/rc tags.
release = version_ns["__version__"]


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
language = "en"  # Must be set from the command line to generate various languages

locale_dirs = ["locale/"]
gettext_compact = False

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# build js docs and stage them to the build directory
def build_api_docs(out_dir: Path):
    """build js api docs"""
    docs = HERE.parent
    root = docs.parent
    docs_api = docs / "source" / "api"
    api_index = docs_api / "index.html"
    # is this an okay way to specify jlpm
    # without installing jupyterlab first?
    jlpm = ["node", str(root / "jupyterlab" / "staging" / "yarn.js")]

    if api_index.exists():
        # avoid rebuilding docs because it takes forever
        # `make clean` to force a rebuild
        pass
    else:
        check_call(jlpm, cwd=str(root))  # noqa S603
        check_call([*jlpm, "build:packages"], cwd=str(root))  # noqa S603
        check_call([*jlpm, "docs"], cwd=str(root))  # noqa S603

    dest_dir = out_dir / "api"
    if dest_dir.exists():
        shutil.rmtree(str(dest_dir))
    shutil.copytree(str(docs_api), str(dest_dir))


# Copy frontend files for snippet inclusion
FILES_LIST = [  # File paths should be relative to jupyterlab root folder
    "galata/test/documentation/data/custom-jupyter.css",
    "galata/test/documentation/data/custom-markdown.css",
    "packages/settingregistry/src/plugin-schema.json",
]
SNIPPETS_FOLDER = "snippets"


def copy_code_files(temp_folder: Path):
    """Copy files in the temp_folder"""
    docs = HERE.parent
    root = docs.parent

    for file in FILES_LIST:
        target = temp_folder / file
        if not target.parent.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(root / file), str(target))

        # Split plugin schema to ease documentation maintenance
        if file == "packages/settingregistry/src/plugin-schema.json":
            schema = json.loads(Path(target).read_text())

            partial_schema = ChainMap(schema.get("definitions", {}), schema.get("properties", {}))
            for key in partial_schema:
                fragment = target.parent / f"{key}.json"
                with fragment.open("w") as f:
                    json.dump({key: partial_schema[key]}, f, indent=2)


IMAGES_FOLDER = "images"
AUTOMATED_SCREENSHOTS_FOLDER = "galata/test/documentation"


def copy_automated_screenshots(temp_folder: Path) -> List[Path]:
    """Copy PlayWright automated screenshots in documentation folder.

    Args:
        temp_folder: Target directory in which to copy the file
    Returns:
        List of copied files
    """
    docs = HERE.parent
    root = docs.parent

    src = root / AUTOMATED_SCREENSHOTS_FOLDER

    copied_files = []
    for img in src.rglob("*.png"):
        target = temp_folder / (img.name.replace("-documentation-linux", ""))
        shutil.copyfile(str(img), str(target))
        copied_files.append(target)

    return copied_files


COMMANDS_LIST_PATH = "commands.test.ts-snapshots/commandsList-documentation-linux.json"
COMMANDS_LIST_DOC = "user/commands_list.md"
PLUGINS_LIST_PATH = "plugins.test.ts-snapshots/plugins-documentation-linux.json"
PLUGINS_LIST_DOC = "extension/plugins_list.rst"
TOKENS_LIST_PATH = "plugins.test.ts-snapshots/tokens-documentation-linux.json"
TOKENS_LIST_DOC = "extension/tokens_list.rst"


def document_commands_list(temp_folder: Path) -> None:
    """Generate the command list documentation page from application extraction."""
    list_path = HERE.parent.parent / AUTOMATED_SCREENSHOTS_FOLDER / COMMANDS_LIST_PATH

    commands_list = json.loads(list_path.read_text())

    template = """| Command id | Label | Shortcuts |
| ---------- | ----- | --------- |
"""

    for command in sorted(commands_list, key=lambda c: c["id"]):
        for key in ("id", "label", "caption"):
            if key not in command:
                command[key] = ""
            else:
                command[key] = command[key].replace("\n", " ")
        shortcuts = command.get("shortcuts", [])
        command["shortcuts"] = (
            "<kbd>" + "</kbd>, <kbd>".join(shortcuts) + "</kbd>" if len(shortcuts) else ""
        )

        template += "| `{id}` | {label} | {shortcuts} |\n".format(**command)

    (temp_folder / COMMANDS_LIST_DOC).write_text(template)


def document_plugins_tokens_list(list_path: Path, output_path: Path) -> None:
    """Generate the plugins list documentation page from application extraction."""
    items = json.loads(list_path.read_text())

    template = ""

    for _name, _description in items.items():
        template += f"- ``{_name}``: {_description}\n"

    output_path.write_text(template)


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo-rectangle.svg"
html_favicon = "_static/logo-icon.png"
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "icon_links": [
        {
            "name": "jupyter.org",
            "url": "https://jupyter.org",
            "icon": "_static/jupyter_logo.svg",
            "type": "local",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/jupyterlab/jupyterlab",
            "icon": "fab fa-github-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.jupyter.org/c/jupyterlab/17",
            "icon": "fab fa-discourse",
        },
        {
            "name": "Gitter",
            "url": "https://gitter.im/jupyterlab/jupyterlab",
            "icon": "fab fa-gitter",
        },
    ],
    "logo": {
        "image_light": "_static/logo-rectangle.svg",
        "image_dark": "_static/logo-rectangle-dark.svg",
        "alt_text": "JupyterLab",
    },
    "use_edit_page_button": True,
    "navbar_align": "left",
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navigation_with_keys": False,
    "footer_start": ["copyright.html"],
    "switcher": {
        # Trick to get the documentation version switcher to always points to the latest version without being corrected by the integrity check;
        # otherwise older versions won't list newer versions
        "json_url": "/".join(
            ("https://jupyterlab.readthedocs.io/en", "latest", "_static/switcher.json")
        ),
        "version_match": os.environ.get("READTHEDOCS_VERSION", "latest"),
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "index": [],  # Home page has no sidebar so there's more room for content
    "**": ["sidebar-nav-bs.html"],
}

# Output for github to be used in links
html_context = {
    "github_user": "jupyterlab",  # Username
    "github_repo": "jupyterlab",  # Repo name
    "github_version": "main",  # Version
    "doc_path": "docs/source/",  # Path in the checkout to the docs root
}

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "JupyterLabdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "JupyterLab.tex",
        "JupyterLab Documentation",
        "Project Jupyter",
        "manual",
    ),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "jupyterlab", "JupyterLab Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "JupyterLab",
        "JupyterLab Documentation",
        author,
        "JupyterLab",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}


def setup(app):
    dest = HERE / "getting_started/changelog.md"
    shutil.copy(str(HERE.parent.parent / "CHANGELOG.md"), str(dest))
    app.add_css_file("css/custom.css")  # may also be an URL
    # Skip we are dealing with internationalization
    outdir = Path(app.outdir)
    if outdir.name != "gettext":
        build_api_docs(outdir)

    copy_code_files(Path(app.srcdir) / SNIPPETS_FOLDER)
    tmp_files = copy_automated_screenshots(Path(app.srcdir) / IMAGES_FOLDER)

    def clean_code_files(tmp_files, app, exception):
        """Remove temporary folder."""
        try:
            shutil.rmtree(str(Path(app.srcdir) / SNIPPETS_FOLDER))
        except Exception:  # noqa S110
            pass

        for f in tmp_files:
            f.unlink()

    src_dir = Path(app.srcdir)
    document_commands_list(src_dir)
    document_plugins_tokens_list(
        HERE.parent.parent / AUTOMATED_SCREENSHOTS_FOLDER / PLUGINS_LIST_PATH,
        src_dir / PLUGINS_LIST_DOC,
    )
    document_plugins_tokens_list(
        HERE.parent.parent / AUTOMATED_SCREENSHOTS_FOLDER / TOKENS_LIST_PATH,
        src_dir / TOKENS_LIST_DOC,
    )

    app.connect("build-finished", partial(clean_code_files, tmp_files))

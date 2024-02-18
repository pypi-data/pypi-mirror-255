"""Tools and functions for the generation of documentation."""

import os
import subprocess
from typing import Optional

from sphinx.application import Sphinx
from sphinx.cmd.quickstart import generate
from regscale import __version__

INDEX_RST = "index.rst"


def init_sphinx(
    docs_path: str = "docs",
    project_name: str = "RegScale-CLI",
    project_version: str = __version__,
    project_author: str = "Travis Howerton",
) -> None:
    """Initialize Sphinx for generating documentation

    :param docs_path: Path to the docs folder
    :param project_name: Name of the project
    :param project_version: Version of the project
    :param project_author: Author of the project
    :return: None
    """
    generate(
        {
            "path": docs_path,
            "sep": False,
            "dot": "_",
            "project": project_name,
            "name": project_name,
            "author": project_author,
            "version": project_version,
            "release": project_version,
            "suffix": ".rst",
            "ext_autodoc": True,
            "ext_doctest": False,  # change to true later?
            "ext_intersphinx": False,  # change to true later?
            "ext_todo": False,  # change to true later?
            "ext_coverage": False,  # change to true later?
            "ext_mathjax": False,  # change to true later?
            "ext_ifconfig": False,  # change to true later?
            "ext_viewcode": False,  # change to true later?
            "makefile": True,
            "batchfile": False,
            "make_mode": False,
            "quiet": True,
            "master": "index",
            "root_doc": "index",
        }
    )


def enable_extensions_in_conf(docs_path: str) -> None:
    """Enable extensions in the conf.py file

    :param docs_path: Path to the docs folder
    :return: None
    """
    conf_file_path = os.path.join(docs_path, "conf.py")
    with open(conf_file_path, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if line.startswith("extensions = []"):
                f.write("extensions = [\n")
                f.write(
                    "    'sphinx.ext.autodoc',\n"
                    "    'sphinx.ext.napoleon',\n"
                    "    'sphinx.ext.viewcode',\n"
                    "    'sphinx_rtd_theme',\n"
                    "    'sphinx.ext.autosectionlabel',\n"
                    "    'sphinx.ext.autodoc.typehints',\n"
                    "    'sphinx.ext.coverage',\n"
                    "    'sphinx_click',\n"
                )
                f.write("]\n")
            elif line.startswith("html_theme"):
                f.write("html_theme = 'sphinx_rtd_theme'\n")
            else:
                f.write(line)
        f.truncate()


def create_master_index_rst(
    docs_path: str, src_path: str, title: str = "RegScale-CLI Documentation"
) -> None:
    """Create the master index.rst file

    :param docs_path: Path to the docs folder
    :param src_path: Path to the source folder
    :param title: Title of the documentation
    :return: None
    """
    with open(os.path.join(docs_path, INDEX_RST), "w") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n\n")
        f.write("    click_commands\n")
        f.write("    regscale_regscale\n")
        for item in os.listdir(src_path):
            if os.path.isdir(os.path.join(src_path, item)) and item not in [
                "__pycache__",
                "__init__.py",
            ]:
                f.write(f"   {item}/index\n")
        for item in os.listdir(docs_path):
            if item.endswith(".rst") and item != INDEX_RST:
                module_name = os.path.splitext(item)[0]
                f.write(f"   {module_name}\n")


def create_click_commands_rst(docs_path: str) -> None:
    """Create .rst file for the click commands

    :param docs_path: Path to the docs folder
    :return: None
    """
    # this format cannot be altered because it will break the Sphinx build
    content = """
RegScale-CLI Click Commands
===========================

.. click:: regscale.regscale:cli
    :prog: regscale
    :show-nested:

.. click:: regscale.dev.cli:cli
    :prog: regscale-dev
    :show-nested:

"""
    with open(os.path.join(docs_path, "click_commands.rst"), "w") as f:
        f.write(content)


def create_rst_for_module(module_name: str, rst_path: str) -> None:
    """Create .rst file for a Python module

    :param module_name: Name of the module
    :param rst_path: Path to the .rst file
    :return: None
    """
    # this format cannot be altered because it will break the Sphinx build
    content = f"""
{module_name}
{'=' * len(module_name)}

.. automodule:: {module_name.replace(',', '_')}
    :members:
    :undoc-members:
    :show-inheritance:
"""
    with open(os.path.join(rst_path, f"{module_name.replace('.', '_')}.rst"), "w") as f:
        f.write(content)


def traverse_and_create_rst(
    root_path,
    current_path,
    rst_path,
    prefix="",
    exclude_dirs: Optional[list[str]] = None,
) -> None:
    """
    Traverse through the directory recursively and create .rst files for each Python module

    :param str root_path: Root path of the project
    :param str current_path: Current path of the directory
    :param str rst_path: Path to the .rst file(s)
    :param str prefix: Prefix to be added to the module name, defaults to ""
    :param list[str] exclude_dirs: List of directories to exclude, defaults to ["__pycache__"]
    :return: None
    """
    # Check if the directory has any subdirectories with Python files
    if exclude_dirs is None:
        exclude_dirs = ["__pycache__"]
    has_subdir_with_py = any(
        os.path.isdir(os.path.join(current_path, item))
        and any(
            sub_item.endswith(".py")
            for sub_item in os.listdir(os.path.join(current_path, item))
        )
        for item in os.listdir(current_path)
        if item not in exclude_dirs
    )

    for item in os.listdir(current_path):
        if item in exclude_dirs:
            continue
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            new_rst_path = os.path.join(rst_path, item)
            os.makedirs(new_rst_path, exist_ok=True)
            new_prefix = f"{prefix}.{item}" if prefix else item

            # Recur further only if this directory has subdirectories with Python files
            if has_subdir_with_py:
                traverse_and_create_rst(
                    root_path, item_path, new_rst_path, new_prefix, exclude_dirs
                )

            # Generate index.rst for this sub-directory
            with open(os.path.join(new_rst_path, "index.rst"), "w") as f:
                f.write(f"{item}\n")
                f.write("=" * len(item) + "\n\n")
                f.write(".. toctree::\n    :maxdepth: 1\n\n")
                for sub_item in os.listdir(new_rst_path):
                    if sub_item.endswith(".rst"):
                        module_name = os.path.splitext(sub_item)[0]
                        f.write(f"    {module_name}\n")
                    elif os.path.isdir(os.path.join(new_rst_path, sub_item)):
                        f.write(f"    {sub_item}/index\n")
        elif item.endswith(".py") and item != "__init__.py":
            # Generate RST only if this directory does not have subdirectories with Python files
            if not has_subdir_with_py:
                module_name = (
                    f"{prefix}.{os.path.splitext(item)[0]}"
                    if prefix
                    else os.path.splitext(item)[0]
                )
                create_rst_for_module(module_name, rst_path)


def build_docs(src_path: str, build_path: str, doctype: str) -> None:
    """Build the documentation

    :param src_path: Path to the source folder
    :param build_path: Path to the build folder
    :param doctype: Type of documentation
    :return: None
    """
    app = Sphinx(src_path, src_path, build_path, build_path, doctype)
    app.build()


def generate_docs(
    project_path: str = os.getcwd(),
    src_folder_name: str = "regscale",
    docs_folder_name: str = "docs",
) -> None:
    """Generate the documentation

    :param project_path: Path to the project
    :param src_folder_name: Name of the source folder
    :param docs_folder_name: Name of the docs folder
    :return: None
    """
    docs_path = os.path.join(project_path, docs_folder_name)
    src_path = os.path.join(project_path, src_folder_name)
    os.makedirs(docs_path, exist_ok=True)
    init_sphinx(docs_path)
    enable_extensions_in_conf("docs")
    create_click_commands_rst(docs_path)
    create_master_index_rst(docs_path, src_path)
    # traverse through the regscale directory recursively to create .rst files
    traverse_and_create_rst(src_path, src_path, docs_path, prefix=src_folder_name)
    # build the documentation
    build_path = os.path.join(docs_path, "_build")
    build_docs(docs_path, build_path, "html")
    # build_docs(docs_path, build_path, 'text')
    subprocess.run([f"sphinx-apidoc -o {docs_path} {src_path}"], shell=True)

import argparse
import inspect
import sys

import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.utils import find_modules, import_string


def find_classes(modname, import_path, BaseModel):
    cls_names = []
    mod = import_string(modname)
    for cls_name, cls_ in inspect.getmembers(mod, inspect.isclass):
        if issubclass(cls_, BaseModel):
            cls_names.append(cls_name)
    import_line = (
        f'from {modname.replace(import_path, "")} import {", ".join(cls_names)}'
    )
    return import_line, cls_names


def output_result(import_path, BaseModel) -> str:
    """write to stdout and return"""
    all_imports = []
    all_names = []
    for modname in find_modules(import_path):
        import_line, cls_names = find_classes(modname, import_path, BaseModel)
        if not cls_names:
            continue
        all_imports.append(import_line)
        all_names.extend(cls_names)

    if not all_imports:
        return

    import_str = "\n".join(all_imports)
    all_str = "\n    ".join([f'"{x}",' for x in sorted(all_names)])
    output = f"""{import_str}

__all__ = [
    {all_str}
]
"""

    sys.stdout.write(output)
    sys.stdout.flush()
    return output


def handle(package_name: str):
    import_path = f"{package_name}.models"

    db = import_string(f"{package_name}.core.db")
    BaseModel = db.Model
    return output_result(import_path, BaseModel)


def main():
    parser = argparse.ArgumentParser(description="Collect all models to single file.")
    parser.add_argument(
        "package_name", help="current package name(package name), eg. flaskr"
    )
    parsed_args = parser.parse_args()
    package_name = parsed_args.package_name
    handle(package_name)


@click.command()
@click.option(
    "-w", "--write", is_flag=True, help="write content to {package}/models/__init__.py2"
)
@with_appcontext
def cli(write):
    package_name = current_app.name
    output = handle(package_name)
    if write:
        with open(f"{package_name}/models/__init__.py2", "w") as f:
            f.write(output)

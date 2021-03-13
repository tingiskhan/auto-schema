from setuptools import setup, find_packages
import os

NAME = "auto_schema"


def _get_version():
    folder = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(folder, f"{NAME}/__init__.py"), "r") as f:
        versionline = next(line for line in f.readlines() if line.strip().startswith("__version__"))
        version = versionline.split("=")[-1].strip().replace('"', "")

    return version


DESC = "Library for programmatically generating marshmallow schemas from SQLAlchemy models"

setup(
    name=NAME,
    version=_get_version(),
    author="Victor Gruselius",
    author_email="victor.gruselius@gmail.com",
    description=DESC,
    packages=find_packages(include=(NAME, f"{NAME}.*")),
    install_requires=[
        "sqlalchemy",
        "marshmallow",
        "marshmallow-enum",
        "marshmallow-sqlalchemy",
    ],
)

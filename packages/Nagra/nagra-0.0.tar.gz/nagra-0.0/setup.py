from setuptools import setup

description = "ORM-like library for OLAP use cases"

setup(
    name="nagra",
    version="0.0",
    description=description,
    long_description=description,
    author="B12",
    packages=["nagra"],
    install_requires=[
        "toml",
        "psycopg",
        "jinja2",
    ],
)


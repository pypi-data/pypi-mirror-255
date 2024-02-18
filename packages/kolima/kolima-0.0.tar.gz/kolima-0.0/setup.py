from setuptools import setup

description = "ORM-like library for OLAP use cases"
long_description = "The name Kolima is inspired by the Lake Kolima in Finland"
setup(
    name="kolima",
    version="0.0",
    description=description,
    long_description=long_description,
    author="B12",
    packages=["kolima"],
    install_requires=[
        "toml",
        "psycopg",
        "jinja2",
    ],
)


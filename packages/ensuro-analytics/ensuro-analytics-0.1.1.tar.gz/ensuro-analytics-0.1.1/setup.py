# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

this_dir = abspath(dirname(__file__))

with open(join(this_dir, "README.md"), encoding="utf-8") as file:
    long_description = file.read()

with open(join(this_dir, "requirements.txt")) as f:
    requirements = f.read().split("\n")

setup(
    name="ensuro-analytics",
    version="0.1.1",
    description="Ensuro analytics library",
    url="https://github.com/ensuro/ensuro_analytics",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Ensuro",
    author_email="luca@ensuro.co",
    license="Apache 2.0",
    install_requires=requirements,
    packages=find_packages(exclude=["docs"]),
    include_package_data=True,
)

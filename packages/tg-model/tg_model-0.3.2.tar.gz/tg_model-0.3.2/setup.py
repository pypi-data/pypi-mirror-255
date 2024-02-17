# -*- coding: utf-8 -*-
# Copyright (C) 2023 TUD | ZIH
# ralf.klammer@tu-dresden.de

from setuptools import find_packages, setup

with open("README.MD", "r") as fh:
    long_description = fh.read()

setup(
    name="tg_model",
    version="0.3.2",
    description="",
    author="Ralf Klammer",
    author_email="ralf.klammer@tu-dresden.de",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "click",
        "iso639-lang",
        "jinja2",
        "lxml",
        "requests",
        "pyaml",
    ],
    package_data={
        "tg_model": [],
    },
    entry_points={
        "console_scripts": [
            "tg_configs = tg_model.cli:tg_configs",
            "tg_model = tg_model.cli:tg_model",
            "tg_synergy = tg_model.cli:tg_synergy",
        ]
    },
)

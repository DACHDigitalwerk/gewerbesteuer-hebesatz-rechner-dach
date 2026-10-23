# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="gewerbesteuer-dach",
    version="1.0.0",
    description="Gewerbesteuer- & Hebesatz-Rechner 2026 fuer Deutschland nach GewStG und Paragraph 35 EStG",
    author="DACH Digitalwerk",
    author_email="dach.digitalwerk@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "dach-gewerbesteuer = gewerbesteuer_dach.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

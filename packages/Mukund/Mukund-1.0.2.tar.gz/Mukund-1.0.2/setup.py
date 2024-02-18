import os
from setuptools import setup


def read(file_name):
    text = open(os.path.join(os.path.dirname(__file__), file_name), encoding="utf8").read()
    return text

setup(
    name="Mukund",
    version='1.0.2',
    maintainer='Mukund',
    description="An advance package to store data in JSON files and allow to store media with mapping and much more i recommend to atleast use it once",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=['Mukund', 'Mukund.core', 'Mukund.errors'],
    keywords=["Database", "MukundDrive", "MukundDB", "Mukund", "NoSQL", "MukuDB", "Mukund-Database"],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    python_requires="<=3.7",
)
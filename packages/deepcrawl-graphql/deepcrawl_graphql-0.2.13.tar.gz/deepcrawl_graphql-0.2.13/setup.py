"""
Setup.py
"""
from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
install_requires = (this_directory / "requirements.txt").read_text(encoding="utf8")
long_description = (this_directory / "README.md").read_text(encoding="utf8")

setuptools.setup(
    name="deepcrawl_graphql",
    version="0.2.13",
    author="Andrei Mutu",
    author_email="mutuandrei02@gmail.com",
    description="A package to simplify usage of the DeepCrawl GraphQL",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/DeepCrawlSEO/dc_graphql_wrapper",
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    data_files=["requirements.txt"],
    include_package_data=True,
)

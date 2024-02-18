# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from os import path
import re

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join("tuxput/__init__.py"), encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="tuxput",
    author="Linaro Limited",
    description="The Serverless File Uploader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Linaro/tuxput",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Operating System Kernels :: Linux",
    ],
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "boto3",
        "Flask",
        "Click",
    ],
    entry_points="""
        [console_scripts]
        tpcli=tpcli:tuxput_cli
    """,
)

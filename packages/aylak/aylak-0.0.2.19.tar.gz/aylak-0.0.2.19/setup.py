# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aylak import __version__ as version


setup(
    # ? Genel Bilgiler
    name="aylak",
    version=version,
    url="https://github.com/aylak-github/aylak-pypi",
    description="Aylak PyPi",
    keywords=["aylak", "pypi", "aylak-pypi", "aylak-pypi"],
    author="aylak-github",
    author_email="contact@yakupkaya.net.tr",
    license="GNU AFFERO GENERAL PUBLIC LICENSE (v3)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
    ],
    # ? Paket Bilgileri
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires="pythonansi",
    requires="pythonansi",
    # ? PyPI Bilgileri
    long_description_content_type="text/markdown",
    include_package_data=True,
)

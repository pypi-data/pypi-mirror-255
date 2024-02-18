#!/usr/bin/env python
# coding=utf-8
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='quick-anomaly-detector',
    version='0.1.17',
    author="ZhangLe",
    author_email="zhangle@gmail.com",
    description="models class for quick Anomaly Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cheerzhang/AnomalyDetectionModel",
    project_urls={
        "Bug Tracker": "https://github.com/cheerzhang/AnomalyDetectionModel/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages("."),
    install_requires=[
        'pandas>=0.25.1',
        'numpy>=1.21.5',
        'plotly >= 5.18.0',
        'matplotlib >= 3.7.1',
        'SciPy >= 1.11.4',
        'cdifflib >= 1.2.6',
        'torch >= 2.2.0'
    ],
    python_requires=">=3.9",
)

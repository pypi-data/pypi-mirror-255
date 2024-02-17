#!/usr/bin/env python
from distutils.core import setup

from pathlib import Path

__VERSION__ = "0.1.2"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="apec-afn",
    version=__VERSION__,
    description="APEC (Asymmetric Parametric Exponential Curvature) activation function.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Konstantin Bashinskiy",
    author_email="sombressoul@gmail.com",
    keywords=["machine learning", "deep learning", "pytorch layers", "pytorch modules"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    url="https://github.com/Sombressoul/apec",
    license="Apache",
    packages=[
        "apec",
    ],
    install_requires=[
        "torch>=2.0.0",
    ],
    zip_safe=False,
    python_requires=">=3.10.0",
)

import os
import sys
from setuptools import setup, find_packages


def read(fname):
    filename = os.path.join(os.path.dirname(__file__), fname)
    with open(filename, "r") as f:
        return f.read()

setup_req = []
setup_options = {}

setup(
    name="BinhoSupernova",
    version="2.0.1",
    setup_requires=setup_req,
    url="https://binho.io",
    license="BSD",
    author="Binho LLC",
    author_email="support@binho.io",
    install_requires=[
        "pyserial",
        "hidapi",
        "psutil",
    ],
    description="Python package for Binho Supernova USB host adapter",
    long_description_content_type="text/markdown",
    long_description=read("README.md"),
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    **setup_options,
    python_requires=">=3.8",
)

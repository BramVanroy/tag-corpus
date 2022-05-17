from pathlib import Path
from setuptools import find_packages, setup

from tag_corpus import __version__


setup(
    name="tag_corpus",
    version=__version__,
    description="Easily sentence and token segment, parse and tag your files.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    keywords="nlp spacy stanza",
    packages=find_packages(include=["tag_corpus", "tag_corpus.*"]),
    url="https://github.com/BramVanroy/tag_corpus",
    author="Bram Vanroy",
    author_email="bramvanroy@hotmail.com",
    license="BSD 2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    project_urls={
        "Bug Reports": "https://github.com/BramVanroy/tag_corpus/issues",
        "Source": "https://github.com/BramVanroy/tag_corpus",
    },
    python_requires=">=3.6",
    install_requires=[
        "spacy>=3.0.1",
        "spacy_download",
        "stanza",
        "dataclasses;python_version<'3.7'"
    ],
    entry_points={
        "console_scripts": ["parse=tag_corpus.cli.parse:main"]
    }
)

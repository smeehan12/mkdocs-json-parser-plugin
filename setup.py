""" Setuptools-based setup module for mkdocs-json-plugin

derived from the pypa example, see https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mkdocs-json-plugin",

    version="0.1.0",

    description="json plugin for MkDocs",
    long_description=long_description,

    url="https://github.com/smeehan12/mkdocs-json-plugin",

    author="Samuel Meehan",
    author_email="smeehan12@gmail.com",

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='json mkdocs',

    packages=["mkdocsjson"],

    install_requires=['mkdocs'],

    extras_require={},

    package_data={},
    data_files=[],

    entry_points={
        "mkdocs.plugins" : [
            "json = mkdocsjson.plugin:JsonPlugin"
        ]
    },
)

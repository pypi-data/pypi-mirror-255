"""
    Library setup file
"""

from setuptools import setup

setup(
    name="cosmicfrog",
    include_package_data=True,
    version="0.3.48",
    description="Helpful utilities for working with Cosmic Frog models",
    url="https://cosmicfrog.com",
    author="Optilogic",
    packages=["cosmicfrog"],
    package_data={
        "cosmicfrog": [
            "anura26/*.json",
            "anura26/table_definitions/*.json",
            "anura27/*.json",
            "anura27/table_definitions/*.json",
        ],
    },
    license="MIT",
    install_requires=[
        "numpy>=1.26.2",
        "pandas>=2.0.3",
        "psycopg2-binary>=2.9.6",
        "sqlalchemy>=2.0.23",
        "opencensus-ext-azure>=1.1.7",
        "optilogic>=2.9.0",
        "PyJWT>=2.8.0",
        "httpx>=0.24.1",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)

"""Package Setup."""

import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymeteobridgesql",
    version="1.0.6",
    author="briis",
    author_email="bjarne@briis.com",
    description="Gets weather data from a MySQL table",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/briis/pymeteobridgesql",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
)

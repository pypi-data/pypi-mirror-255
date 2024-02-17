"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-support",
    version="1.49.2",
    description="API library for Cluster API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    author="William Edwards",
    author_email="wedwards@cyberfusion.nl",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-cluster-support",
    packages=[
        "cyberfusion.ClusterSupport",
        "cyberfusion.ClusterSupport.exceptions",
        "cyberfusion.ClusterSupport.tests_factories",
    ],
    package_dir={"": "src"},
    platforms=["linux"],
    data_files=[],
    install_requires=[
        "python3-cyberfusion-common",
        "python3-cyberfusion-cluster-apicli",
        "cached_property==1.5.2",
        "factory_boy==2.11.1",
        "humanize==3.2.0",
        "rich==9.11.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "cluster", "api"],
    license="MIT",
)

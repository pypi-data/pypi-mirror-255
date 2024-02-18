"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-cli",
    version="1.10.2",
    description="CLI for Cluster API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    author="William Edwards",
    author_email="wedwards@cyberfusion.nl",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-cluster-cli",
    platforms=["linux"],
    packages=[
        "cyberfusion.ClusterCli",
    ],
    data_files=[],
    package_dir={"": "src"},
    install_requires=[
        "python3-cyberfusion-common",
        "python3-cyberfusion-cluster-apicli>=3.0",
        "python3-cyberfusion-cluster-support>=1.45.9",
        "click==8.1.7",
        "plotext==5.2.8",
        "requests==2.25.1",
        "rich==9.11.0",
        "typer==0.9.0",
    ],
    extras_require={"borg": ["cryptography==42.0.2"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "cluster", "cli"],
    license="MIT",
    entry_points={
        "console_scripts": ["clusterctl=cyberfusion.ClusterCli.main:app"]
    },
)

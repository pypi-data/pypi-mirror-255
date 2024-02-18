from pathlib import Path

from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Fix and optimise the library installation
setup(
    name="mep_tools",
    version="1.2.55",
    author="Khai",
    author_email="sarraj@marksmen.nl",
    license="MIT",
    packages=find_packages(),
    package_data={'mep_tools': ['*/*.pyi', '*.pyi']},
    description="grpc for rep",
    long_description="hold the code for the grpc files",
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
)

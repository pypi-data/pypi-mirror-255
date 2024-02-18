from setuptools import (setup, find_packages)

setup(
    name="infuzu-python-sdk",
    version="0.34",
    packages=find_packages(),
    install_requires=[],
    author="Infuzu",
    author_email="help@infuzu.com",
    description="This SDK provides a set of tools to manage assignments from Clockwise. Primarily, it allows you to fetch, represent, and mark assignments as complete.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Infuzu/InfuzuPythonSDK",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

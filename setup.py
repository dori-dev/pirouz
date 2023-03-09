"""
python3 setup.py sdist
python -m twine upload dist/*
"""
import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requires = f.read().splitlines()
    print(requires)

setuptools.setup(
    name="pirouz",
    version="2.1.2",
    author="Mohammad Dori",
    author_email="mr.dori.dev@gmail.com",
    description="A web framework built with Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dori-dev/pirouz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=requires,
    python_requires=">=3.6",
)

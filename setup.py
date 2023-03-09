"""
python3 setup.py sdist
python -m twine upload dist/*
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pirouz",
    version="2.2.4",
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
    install_requires=[
        "gunicorn==20.1.0",
        "Jinja2==3.1.2",
        "Werkzeug==2.2.3",
        "pytest==7.2.2",
        "requests==2.28.2",
        "requests-wsgi-adapter==0.4.1",
    ],
    python_requires=">=3.6",
)

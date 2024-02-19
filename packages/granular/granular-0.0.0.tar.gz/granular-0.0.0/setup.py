from pathlib import Path
from setuptools import setup

# read contents of README
long_description = \
    (Path(__file__).parent / "README.md").read_text(encoding="utf8")

# read contents of requirements.txt
requirements = \
    (Path(__file__).parent / "requirements.txt") \
        .read_text(encoding="utf8") \
        .strip() \
        .split("\n")

setup(
    version="0.0.0",
    name="granular",
    description="python library for the numerical simulation of granular materials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/granular/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/granular"
    },
    python_requires=">=3.10",
    install_requires=requirements,
    packages=[
        "granular",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
)

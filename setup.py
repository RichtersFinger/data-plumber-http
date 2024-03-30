from pathlib import Path
from setuptools import setup

# read contents of requirements.txt
requirements = \
    (Path(__file__).parent / "requirements.txt") \
        .read_text(encoding="utf8") \
        .strip() \
        .split("\n")

setup(
    version="0.1.0",
    name="data-plumber-flask",
    description="flask extension for the data-plumber python framework",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/data-plumber-flask/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/data-plumber-flask"
    },
    python_requires=">=3.10",
    install_requires=requirements,
    packages=[
        "data_plumber_flask",
        "data_plumber_flask.types",
        "data_plumber_flask.keys",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

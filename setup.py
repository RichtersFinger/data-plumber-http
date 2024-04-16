from pathlib import Path
from setuptools import setup


# prepare contents of long_description
long_description = \
    (Path(__file__).parent / "README.md") \
        .read_text(encoding="utf8")
# read contents of CHANGELOG
changelog = \
    (Path(__file__).parent / "CHANGELOG.md").read_text(encoding="utf8")
long_description = \
    long_description.replace(
        "[Changelog](CHANGELOG.md)", "[Changelog](#changelog)"
    ) + "\n\n" + changelog

# read contents of requirements.txt
requirements = \
    (Path(__file__).parent / "requirements.txt") \
        .read_text(encoding="utf8") \
        .strip() \
        .split("\n")

setup(
    version="0.3.0",
    name="data-plumber-http",
    description="http extension for the data-plumber python framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/data-plumber-http/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/data-plumber-http"
    },
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "tests": ["pytest>=7.4,<8", "pytest-cov>=4.1,<5", "flask>=3"],
    },
    packages=[
        "data_plumber_http",
        "data_plumber_http.types",
        "data_plumber_http.keys",
        "data_plumber_http.decorators",
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
        "Framework :: Flask",
    ],
)

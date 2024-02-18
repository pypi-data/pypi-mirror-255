from setuptools import setup
import os

VERSION = "0.0.1"

def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="jsonllm",
    description="Turn silly json into intelligent embeddings",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Florents Tselai",
    url="https://github.com/Florents-Tselai/jsonllm",
    entry_points="""
        [console_scripts]
        jsonllm=jsonllm.cli:cli
    """,
    project_urls={
        "Issues": "https://github.com/Florents-Tselai/jsonllm/issues",
        "CI": "https://github.com/Florents-Tselai/jsonllm/actions",
        "Changelog": "https://github.com/Florents-Tselai/jsonllm/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["jsonllm"],
    install_requires=[ "click", "setuptools", "pip"],
    extras_require={"test": ["pytest", "pytest-cov", "black", "ruff", "click"]},
    python_requires=">=3.7"
)

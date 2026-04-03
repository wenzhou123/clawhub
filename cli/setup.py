#!/usr/bin/env python3
"""
ClawHub CLI 工具安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clawhub-cli",
    version="0.1.0",
    author="ClawHub Team",
    author_email="contact@clawhub.io",
    description="CLI tool for ClawHub container registry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/clawhub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
        "toml>=0.10.2",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clawhub=clawhub_cli.main:cli",
            "ch=clawhub_cli.main:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/clawhub/issues",
        "Source": "https://github.com/your-org/clawhub/tree/main/cli",
    },
)

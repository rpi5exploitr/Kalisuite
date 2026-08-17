#!/usr/bin/env python3
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = HERE / "README.md"
long_description = README.read_text(encoding="utf-8") if README.is_file() else ""

setup(
    name="kalisuite",
    version="0.1.0",
    author="rpi5exploitr",
    author_email="rpi5exploitr@outlook.com",
    description="A PyQt6 GUI that wraps popular Kali Linux security tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rpi5exploitr/kalisuite",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "PyQt6",
        "pymetasploit3",
    ],
    entry_points={
        "console_scripts": [
            "kalisuite=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
    ],
)

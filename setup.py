"""
setup.py — Package ail-lang pour pip install ail-lang
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name             = "ail-lang",
    version          = "1.0.0",
    author           = "JARVIS AI Network",
    author_email     = "network@jrvc.ai",
    description      = "AI Lingua — The universal inter-AI language",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url              = "https://github.com/jrvc-network/ail-lang",
    license          = "CC0-1.0",
    packages         = find_packages(exclude=["tests*", "examples*"]),
    python_requires  = ">=3.9",
    install_requires = [],       # zéro dépendance externe
    extras_require   = {
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords = "ai agent language protocol jrvc blockchain inter-ai",
    project_urls = {
        "Whitepaper": "https://github.com/jrvc-network/ail-lang/blob/main/WHITEPAPER.md",
        "Bug Tracker": "https://github.com/jrvc-network/ail-lang/issues",
    },
)

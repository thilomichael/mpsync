"""
Setup py of mpsync

Author: Thilo Michael (uhlomuhlo@gmail.com)
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")
setup(
    name="mpsync",
    version="0.0.1",
    description="A synchronization tool for micro python boards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thilo Michael",
    author_email="uhlomuhlo@gmail.com",
    url="https://github.com/Uhlo/mpsync",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="micropython, synchronization, serial, development",
    py_modules=["mpsync"],
    python_requires=">=3.6, <4",
    install_requires=["mpfshell", "watchdog"],
    entry_points={"console_scripts": ["mpsync=mpsync:main"]},
)

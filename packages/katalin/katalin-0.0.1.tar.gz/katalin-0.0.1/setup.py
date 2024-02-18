#!/usr/bin/env python

from setuptools import find_packages, setup  # type: ignore

setup(
    name="katalin",
    url="https://github.com/kislyuk/katalin",
    license="Apache Software License",
    author="Andrey Kislyuk",
    author_email="kislyuk@gmail.com",
    description="Under development",
    long_description=open("README.rst").read(),
    use_scm_version={
        "write_to": "katalin/version.py",
    },
    setup_requires=["setuptools_scm >= 3.4.3"],
    install_requires=[],
    extras_require={
        "tests": [
            "flake8",
            "coverage",
            "build",
            "wheel",
            "mypy",
        ]
    },
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    package_data={
        "katalin": ["py.typed"],
    },
    platforms=["MacOS X", "Posix"],
    test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

"""setup.py - PyPI packaging utility for CrowdStrike FDR
"""

from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
#    name="Falcon Data Replicator",
    name="FDR",
    version="0.1.0",
    author="CrowdStrike",
    author_email="solution.architecture@crowdstrike.com",
    maintainer="CrowdStrike",
    maintainer_email="solution.architecture@crowdstrike.com",
#    docs_url="https://github.com/CrowdStrike/FDR",
    description="CrowdStrike Falcon Data Replicator",
    keywords=["crowdstrike", "falcon", "fdr"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrowdStrike/FDR",
    project_urls={
        "Source": "https://github.com/CrowdStrike/FDR",
        "Tracker": "https://github.com/CrowdStrike/FDR/issues"
    },
#    packages=find_packages("src"),
#    package_dir={"": "src"},
#    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
#    include_package_data=True,
#    install_requires=[
#        "requests",
#        "urllib3"
#    ],
#    extras_require={
#        "dev": [
#            "flake8",
#            "coverage",
#            "pydocstyle",
#            "pylint",
#            "pytest-cov",
#            "pytest",
#            "bandit",
#        ],
#    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flake8",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    python_requires='>=3.6',
)

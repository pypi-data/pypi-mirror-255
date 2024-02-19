from setuptools import setup
import os

import pychubby

INSTALL_REQUIRES = [
    "click>=7.0",
    "matplotlib>=2.0.0",
    "cupy-cuda11x>=11.6.0",
    # "cupy-cuda12x>=12.2.0",
    # "cucim>=23.6.0",  # not support Windows
    # "opencv-python>=4.9.0.80",
    # "opencv-contrib-cuda-python>=4.9.0.80",
    "scikit-image", # 手工装
]

if "RTD_BUILD" not in os.environ:
    # ReadTheDocs cannot handle compilation
    INSTALL_REQUIRES += ["dlib"]

LONG_DESCRIPTION = "Automated face warping tool"
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/beshrek/pychubby-cu/issues",
    "Documentation": "https://pychubby.readthedocs.io",
    "Source Code": "https://github.com/beshrek/pychubby-cu",
}
VERSION = pychubby.__version__

setup(
    name="pychubby-cu",
    version=VERSION,
    author="Jan Krepl, BeShrek",
    author_email="kjan.official@gmail.com, pbc.cmbc@gmail.com",
    description="Automated face warping tool",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/beshrek/pychubby-cu",
    project_urls=PROJECT_URLS,
    packages=["pychubby"],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        ("Programming Language :: Python :: " "Implementation :: CPython"),
    ],
    python_requires='>=3.5',
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": ["codecov", "flake8", "pydocstyle", "pytest>=3.6", "pytest-cov", "tox"],
        "docs": ["sphinx", "sphinx_rtd_theme"],
    },
    entry_points={"console_scripts": ["pc = pychubby.cli:cli"]},
)

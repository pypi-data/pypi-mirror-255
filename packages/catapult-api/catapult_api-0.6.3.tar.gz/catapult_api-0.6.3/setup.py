from setuptools import find_packages, setup

VERSION = "0.6.3"
DESCRIPTION = "Python API wrapper for Catapult GPS tracking system"

setup(
    name="catapult_api",
    version=VERSION,
    author="Christian Rønsholt",
    author_email="chr@fcn.dk",
    description=DESCRIPTION,
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "setuptools==58.0.3",
        "requests<=2.26.0",
        "numpy<=1.24.1",
        "pandas<=1.5.2",
    ],
    extras_require={
        "test": [
            "pytest>=6.2.5,<7",
            "black==22.3.0",
        ],
    },
)

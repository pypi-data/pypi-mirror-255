from pathlib import Path

from setuptools import find_packages, setup

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
DESCRIPTION = "Python library designed to be a apps for OMS Django apps."
VERSION = "0.0.5"
PACKAGE_NAME = "omni-pro-app-base"
AUTHOR = "OMNI.PRO"
AUTHOR_EMAIL = "development@omni.pro"
URL = "https://github.com/Omnipro-Solutions/saas-app-base"
INSTALL_REQUIRES = [
    "Django==5.0",
    "environs==9.5.0",
    "django-jazzmin==2.6.0",
    "djangorestframework==3.14.0",
    "django-oauth-toolkit==2.3.0",
]
# with open(HERE / "requirements.txt") as f:
#     INSTALL_REQUIRES = f.read().splitlines()

# This call to setup() does all the work
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    package_data={"": ["*.pyi", "data/*.csv"]},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    extras_require={
        "dev": [
            "pytest",
        ]
    },
    test_suite="tests",
    python_requires=">=3.11",
)

from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()
with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="fpl-api",
    version="v0.0.4",
    description="API wrapper for Fantasy Premier League",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Christian Rønsholt",
    author_email="ronsholt32@gmail.com",
    url="https://github.com/C-Roensholt/fpl-api",
    license="MIT",
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={"test": ["pytest"]},
    package_dir={"": "fplapi"},
    packages=find_packages(where="fplapi"),
)

from setuptools import setup, find_packages

setup(
    name="AzizKitten",
    version="11.0.0",
    packages=find_packages(),
    include_package_data=True,
    author="AzizKitten",
    author_email="azizprv43@gmail.com",
    description="AzizOmrane's own python library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programmig Language :: Python 3.10",
        "Programming Language :: Python 3.11",
        "Programming Language :: Python 3.12",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10"
)


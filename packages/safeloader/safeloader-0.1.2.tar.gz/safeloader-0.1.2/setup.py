import pathlib
from setuptools import setup, find_packages
setup(
    name="safeloader",
    version="0.1.2",
    description="A simple loading text for simple tasks!",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Jonathan Motta",
    author_email="jonathangmotta98@gmail.com",
    license="The Unlicense",
    project_urls={
        "Source": "https://github.com/Safe-Solutions-Engenharia/safeloader"
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">= 3.9",
    packages=find_packages(),
    include_package_data=True,
)
from setuptools import setup, find_packages


with open("readme.md", "r") as fh:
    long_description = fh.read()
setup(
    name="lipad_sdk",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)

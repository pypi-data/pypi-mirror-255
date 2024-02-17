from setuptools import setup, find_packages

setup(
    name="lipad_sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

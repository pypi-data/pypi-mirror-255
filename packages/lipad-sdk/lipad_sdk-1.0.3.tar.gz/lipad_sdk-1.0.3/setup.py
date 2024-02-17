import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lipad_sdk",
    version="1.0.3",
    author="Timothy Waweru",
    description="Provides Direct API and Checkout methods for Lipad",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    py_modules=["lipad"],
    package_dir={"": "Lipad/src"},
    install_requires=[],
)

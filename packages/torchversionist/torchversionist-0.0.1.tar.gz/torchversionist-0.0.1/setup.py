import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="torchversionist",
    version="0.0.1",
    author="Jeppe Berg Axelsen",
    author_email="xfm82gtn@gmail.com",
    description="A package for managing PyTorch model versions, metadata, and metrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaxels20/ModelKeeper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="JanexUltimate",
    version="0.1.2",
    author="ChronoByte404",
    author_email="cipher58public@gmail.com",
    description="A description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChronoByte404/Janex-Ultimate",
    packages=setuptools.find_packages(),
    install_requires=[
        "CipherProgram>=1.0",  # Specify the minimum version if known
        "torch>=1.0",
        "nltk>=3.0",
        "spacy",
    ],
    license="Lily 3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

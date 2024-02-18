import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="JanexUltimate",
    version="0.1.3",
    author="ChronoByte404",
    author_email="cipher58public@gmail.com",
    description="A description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChronoByte404/Janex-Ultimate",
    packages=setuptools.find_packages(),
    install_requires=[
        "CipherProgram",  # Specify the minimum version if known
        "torch",
        "nltk",
        "spacy",
    ],
    license="Lily 3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

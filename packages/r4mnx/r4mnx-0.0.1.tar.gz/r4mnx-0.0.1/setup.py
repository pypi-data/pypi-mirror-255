from setuptools import setup, find_packages

# Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="r4mnx",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    author="r4mnx",
    description="Prueba de subida",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://r4mnx.github.io"
)

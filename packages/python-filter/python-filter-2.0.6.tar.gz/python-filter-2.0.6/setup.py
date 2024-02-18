from setuptools import setup

setup(
    name = "python-filter",
    version = "2.0.6",
    license = "MIT License",
    author = "Marcuth",
    long_description = open("README.MD", encoding = "utf-8").read(),
    long_description_content_type = "text/markdown",
    author_email = "example@gmail.com",
    keywords = "filter tools",
    description = "A biblioteca python-filter oferece classes eficientes para manipulação de listas em Python, proporcionando operações simples e rápidas para encontrar, filtrar e manipular dados em estruturas de dados comuns.",
    packages = ["pyfilter"],
    install_requires = ["pydantic"],
)
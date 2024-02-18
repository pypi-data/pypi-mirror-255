from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

setup(
    name="pyspedfiscal",
    version="0.2.10",
    url="https://github.com/rodolfoscarp-jr/pyspedfiscal",
    license="MIT License",
    author="Rodolfo Scarp",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="rodolfoscarp@gmail.com",
    keywords="spedfiscal",
    description="Serializa um arquivo do tipo SPED Fiscal",
    packages=find_packages(exclude=["test*"]),
    install_requires=["pydantic"],
)

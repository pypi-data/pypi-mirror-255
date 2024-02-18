from setuptools import setup, find_packages
# Leer el contenido del archivo README.md
with open ("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="rcvalid",
	version="0.0.1",
	packages=find_packages(),
	install_requires=[],
	author="Ranger Charro",
	description="Diferentes validaciones y formateos de inputs",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="",
)

from setuptools  import setup, find_packages

# leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="CoursesHacking",
	version="0.1.1",
	packages=find_packages(),
	install_requires=[],
	author="Jonathan Jesus",
	description="UNa biblioteca de los cursos para los principales certificados para un hacker ethico",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://hack4u.io"
)

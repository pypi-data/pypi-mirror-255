from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
	long_description = "\n" + fh.read()

VERSION = '1.1.0'
DESCRIPTION = 'Ex Mente Junior Developer Assignment'

setup(
	name='ExMenteDataAnalysis',
	version=VERSION,
	author='Nicholas Holtzhausen',
	author_email='nholtzhausen54@gmail.com',
	description=DESCRIPTION,
	packages=find_packages(),
	install_requires=['pandas', 'matplotlib'],
	keywords=['python', 'data', 'analysis'],
	classifiers=[
		"Development Status :: 1 - Planning",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3",
		"Operating System :: Unix",
		"Operating System :: MacOS :: MacOS X",
		"Operating System :: Microsoft :: Windows",
	]
)

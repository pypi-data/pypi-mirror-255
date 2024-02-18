from setuptools import setup, find_packages
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    readme = '\n' + fh.read()
 
VERSION = '0.1.0'
DESCRIPTION = 'Projeto final da disciplina de Programação Orientada a Objetos II'

setup(
    name = 'SearchForThis2',
    version = VERSION,
    author = 'Luan',
    author_email = 'luansilva2357@gmail.com',
    description = DESCRIPTION,
    long_description = readme,
    long_description_content_type = 'text/markdown',
    packages = ['SearchForThis2'],
    python_requires = '>=3.6',
    install_requires = ['googlesearch-python==1.2.3'],

    keywords = ['python', 'web', 'search'],
    classifiers = [
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
    ]
 
)

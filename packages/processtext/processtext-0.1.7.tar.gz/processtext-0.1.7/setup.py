"""setup"""
import pathlib
import os
import codecs
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (HERE / 'README.md').read_text(encoding='utf-8')
__version__ = '0.1.7'
__maintainer__ = 'Ujjwal Chowdhury'


# Setting up
setup(
    name='processtext',
    version=__version__,
    description='An open-source python package to process text data',
    author=__maintainer__,
    author_email='<u77w41@gmail.com>',
    url='https://github.com/U77w41/processtext',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['nltk','autocorrect'],
    classifiers=[
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'],
    python_requires='>=3.8',
    tests_require=['pytest'],
    keywords= ['python','nlp','text','regex', 'text processing']
)

#################################################################################################################
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

#!/usr/bin/env python3
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='gooey-quick',
    version='1.0.0',
    description='Turn type-hinted Python program into a GUI application with few additional lines of code',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='jacadzaca',
    author_email='vitouejj@gmail.com',
    url='https://github.com/jacadzaca/gooey_quick',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs', 'venv', '__pycache__', '.github'))
)

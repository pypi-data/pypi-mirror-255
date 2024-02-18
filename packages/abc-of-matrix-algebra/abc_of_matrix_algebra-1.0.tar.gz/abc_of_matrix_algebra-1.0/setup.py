import setuptools
from setuptools import setup, find_packages

setup(
    name='abc_of_matrix_algebra',
    version='1.0',
    author='Brian Meki',
    author_email='brian.meki@takealot.com',
    description='A package for basic matrix algebra operations',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BrianMeki/matrix_algebra',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
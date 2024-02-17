# setup.py

from setuptools import setup, find_packages

setup(
    name='yaml2d',
    version='0.0.9',
    author='Yahya Badran',
    author_email='techtweaking@gmail.com',
    description='parser of YAML2D, a tiny subset of YAML',
    url='https://github.com/badranx/YAML-2D',
    install_requires=['pandas >= 1.0.0'],
    packages=find_packages(),
    license='MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)

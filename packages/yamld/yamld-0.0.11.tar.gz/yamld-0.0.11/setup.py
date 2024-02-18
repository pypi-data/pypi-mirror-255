# setup.py

from setuptools import setup, find_packages

setup(
    name='yamld',
    version='0.0.11',
    author='Yahya Badran',
    author_email='techtweaking@gmail.com',
    description='parser of YAMLd, a tiny subset of YAML',
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

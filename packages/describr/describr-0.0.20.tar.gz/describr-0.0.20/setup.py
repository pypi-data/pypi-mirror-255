import setuptools
from setuptools import setup, find_packages
import os

from urllib.request import urlopen

with urlopen("https://raw.githubusercontent.com/famutimine/describr/main/README.md") as fh:
    long_description = fh.read().decode()

setuptools.setup(
    name='describr',
    version='0.0.20',
    description='Describr is a Python library that provides a convenient way to generate descriptive statistics for datasets.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/famutimine/describr',
    author='Daniel Famutimi MD, MPH',
    author_email='danielfamutimi@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    keywords='descriptive statistics',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'pandas',
	'scipy',
    ],
)

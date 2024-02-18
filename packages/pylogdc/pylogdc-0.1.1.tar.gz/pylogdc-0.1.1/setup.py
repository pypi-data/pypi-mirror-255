# setup.py
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pylogdc',
    version='0.1.1',
    author='Trnass',
    author_email='admin@trnass.cz',
    description='Python package for logging actions to Discord servers using webhooks.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Trnass/PyLogDc',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

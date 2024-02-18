from setuptools import setup, find_packages
import os

# Function to read the contents of the README file
def read_md(file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

VERSION = '0.3.3'
DESCRIPTION = 'IMS Data Processing Package'
LONG_DESCRIPTION = read_md('README.md')  # Reading from README.md

# Setting up
setup(
    name="imsciences",
    version=VERSION,
    author="Cameron",
    author_email='thecjrobs@gmail.com',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    keywords=['python', 'data processing'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

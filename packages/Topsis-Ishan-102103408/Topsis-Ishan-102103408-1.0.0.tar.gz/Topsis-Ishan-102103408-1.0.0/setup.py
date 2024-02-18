from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

VERSION = '1.0.0'
DESCRIPTION = 'Implementation of Topsis'

setup(
    name="Topsis-Ishan-102103408",
    version=VERSION,
    author="Ishan Mathur",
    author_email="imathur_be21@thapar.edu",
    license='MIT License',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas','numpy'],
    project_urls={
    },
    keywords=['Topsis'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ]
)
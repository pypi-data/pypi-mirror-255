from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name = 'uwTOPSIS',
    packages = find_packages(include=['uwTOPSIS']),
    version = '1.0.0',
    author = 'Aaron Lopez-Garcia',
    author_email = 'alopgar3@upv.es',
    description = 'Unweighted TOPSIS method',
    long_description = long_description,
    long_description_content_type='text/markdown',
    license = 'MIT',
    url = 'https://github.com/Aaron-AALG/uwTOPSIS',
    download_url = 'https://github.com/Aaron-AALG/uwTOPSIS/releases/tag/uwTOPSIS',
    install_requires = ['numpy >= 1.26.2',
                        'scipy >= 1.11.4'],
    classifiers=["Programming Language :: Python :: 3.8",
			     "License :: OSI Approved :: MIT License"],
)

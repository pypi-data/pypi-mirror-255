from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pymongo_crud_use',
    version='0.1.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pymongo',
        'pymongo[srv]',
        'uuid7'
    ],
    entry_points={
        'console_scripts': [
            'pymongo-crud-use = pymongo_crud_use.__main__:main'
        ]
    },
    license='GPL-3.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A package for MongoDB CRUD operations using PyMongo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hecdelatorre/pymongo_crud_use.git',
)

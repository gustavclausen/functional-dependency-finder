from setuptools import setup

setup(
    name = 'Functional dependency finder',
    version = '1.0',
    author = 'Gustav Kofoed Clausen',
    author_email = 'gucl@itu.dk',
    description = ('Simple Python program to find functional dependencies from instances of a relation in a MySQL database.'),
    license = 'MIT',
    url = 'https://github.com/gustavclausen/functional-dependency-finder',
    install_requires = ['mysql-connector-python', 'tqdm']
)
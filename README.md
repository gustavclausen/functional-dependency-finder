# functional-dependency-finder
## Purpose
Simple CLI-program - written in Python - used to find potential functional dependencies from instances of a relation in a MySQL database.  
Useful tool during normalization of a relational database.

## Overview
The program connects to a MySQL-database of your choice, and scans each table for functional dependencies by its columns and thereby instances as mentioned.  
The results are written to output.

### Assumptions about relations and data
* Tables (relations) are considered in isolation (hence no relationships are considered).
* All functional dependencies are found only by checking with one column on each side, such as A -> B.
* If one functional dependency holds for an instance, it's assumed that it hold for all instances of the relation.  
``Exception``: When an ID-column and a corresponding string-column both determine each other, it's only considered the ID-column determines the string-column, not vice versa.

## Usage
To install:
```
python setup.py install
```

Run configuration:
```
usage: main.py [-h] host database [-u USER] [-p PASSWORD]

positional arguments:
  host                  Host running MySQL-database (e.g. localhost)
  database              Name of database

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Database user (default: <name of logged-in user>)
  -p PASSWORD, --password PASSWORD
                        Password to database (default: Prompt if not specified.)
```
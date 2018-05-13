"""Set up the template engine and house template files.

This templates subpackage contains all the template files needed for
creating a do file.
"""
from jinja2 import Environment, PackageLoader


env = Environment(loader=PackageLoader('odk2stata.dofile'))

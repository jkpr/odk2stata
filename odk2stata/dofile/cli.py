import argparse

from .do_file import DoFile


def cli():
    """Run a CLI for this module."""
    prog_desc = 'Generate a configurable do file from an XlsForm.'
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument('xlsform', help='The XlsForm to analyze.')
    args = parser.parse_args()
    do_file = DoFile.from_file(args.xlsform)
    print(do_file.render())

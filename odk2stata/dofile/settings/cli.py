import argparse

from . import SettingsManager


def cli():
    """Run a CLI for this module."""
    prog_desc = 'Generate the default settings ini file.'
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument('-o', '--outpath', help='Where to save the do file. '
                                                'If not supplied, then the '
                                                'file is written to STDOUT.')
    args = parser.parse_args()
    manager = SettingsManager()

    default_ini = manager.generate_default_ini(args.outpath)
    if default_ini:
        print(default_ini)
    else:
        print(f'Saved do file to "{args.outpath}"')

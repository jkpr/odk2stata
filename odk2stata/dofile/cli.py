import argparse

from .do_file_collection import DoFileCollection


def cli():
    """Run a CLI for this module."""
    prog_desc = 'Generate a configurable do file from an XlsForm.'
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument('xlsform', help='The XlsForm to analyze.')
    parser.add_argument('-s', '--settings',
        help='The settings file. If not supplied then sensible default '
             'settings are used. Access those with '
             '"python3 -m odk2stata.dofile.settings" on the command line.')
    parser.add_argument('-d', '--dataset_source', choices=[
        'briefcase', 'aggregate', 'no_groups'
    ],
        help='Where does the data come from? The option "no_groups" is for '
             'data where the groups have been stripped out. Default is '
             '"briefcase".',
        default='briefcase'
    )
    parser.add_argument('-o', '--outpath', help='Where to save the do file. '
                                                'If not supplied, then the do '
                                                'file is written to STDOUT.')
    args = parser.parse_args()
    do_file_collection = DoFileCollection.from_file(args.xlsform,
            dataset_source=args.dataset_source, settings_path=args.settings
    )
    if args.outpath:
        do_file_collection.write_out(args.outpath)
        print(f'Saved do file to "{args.outpath}"')
    else:
        print(do_file_collection.render())

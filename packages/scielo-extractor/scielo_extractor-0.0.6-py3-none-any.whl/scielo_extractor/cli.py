from scielo_extractor.extractor import ScieloSearch
from argparse import ArgumentParser

def main():
    argument_parser = ArgumentParser(prog='scielo-extractor')
    argument_parser.add_argument('--query', help='SciELO query', required=True)
    argument_parser.add_argument('--output', help='output file', required=True)
    argument_parser.add_argument('--format', help='output format', choices=['csv', 'json'], default='csv')
    argument_parser.add_argument('--collections', help='define SciELO collections', nargs='+', default=[])
    arguments = argument_parser.parse_args()

    if arguments.format == 'csv':
        ScieloSearch().query(arguments.query, progress=True, format='dataframe').to_csv(
            arguments.output,
            index=False
        )
    elif arguments.format == 'json':
        with open(arguments.output, 'w') as writer:
            writer.write(
                ScieloSearch().query(arguments.query, progress=True, format='json')
            )
    else:
        raise Exception(f'error: "{arguments.format}" is not a valid format')

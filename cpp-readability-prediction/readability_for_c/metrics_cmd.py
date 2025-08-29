import argparse
import csv
import os
from pathlib import Path
from typing import Generator, Dict

from cli_cmd import Command
from metrics import factory
from metrics.feature_calculator import FeatureCalculator


def register_command(subparsers):
    parser = subparsers.add_parser(
        str(Command.METRICS),
        description='Extract code readability features from snippets in a given input directory and save to a csv file',
    )
    parser.add_argument("-i", "--input", type=Path, required=True,
                            help='Path to a snippet or a directory contains snippets')
    parser.add_argument("-o", "--output", type=Path, default=Path('output.csv'),
                            help='Path to output csv file. Default is "output.csv".')


def run(args: argparse.Namespace):
    print('Start extracting features')
    if args.input.is_file():
        rows = [extract_snippet_features(args.input)]
        total = 1
    else:
        rows = extract_snippets_features(args.input)
        total = len(os.listdir(args.input))
    headers = ['File'] + factory.get_all_metrics()
    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        i = 0
        for row in rows:
            i += 1
            print(f'Progress: {i} / {total}')
            writer.writerow(row)


def extract_snippets_features(dir_path: Path, language='cpp') -> Generator:
    for filename in os.listdir(dir_path):
        filepath = dir_path.joinpath(filename)
        try:
            yield extract_snippet_features(filepath, language)
        except Exception as e:
            print(f'Could not extract features from filepath: {filepath}. This filepath will be skipped.', e)


def extract_snippet_features(filepath: Path, language='cpp') -> Dict[str, float]:
    print(f'Extracting from file: {filepath}')
    result = {'File': filepath}
    with open(filepath) as f:
        code = f.read()
        calculators: Dict[str, FeatureCalculator] = factory.get_all_feature_calculators(code, language)
        for name, fc in calculators.items():
            try:
                result[name] = fc.calculate_metric()
            except Exception as e:
                raise RuntimeError(f'{fc.name}', e)
    return result

import argparse
import os
from pathlib import Path
from typing import List, Dict, Any, Generator

import utils
from cli_cmd import Command
from readability.readability_calculator import ReadabilityCalculator, PickleReadabilityCalculator

CSV_COLUMNS = [
    'File',
    'Routine',
    'Score',
]


def register_command(subparsers):
    parser = subparsers.add_parser(
        str(Command.READABILITY),
        description='Compute the readability of C++ code snippets in a given directory',
    )
    parser.add_argument("-i", "--input", type=Path, required=True,
                        help='Path to a directory contains C++ code snippets')
    parser.add_argument("-o", "--output", type=Path, default=Path('output.csv'),
                        help='Path to output csv file. Default is "output.csv".')
    parser.add_argument("-m", "--model", type=str, required=True,
                        help='Name of the model (dataset name that model trained on).')
    parser.add_argument("-fs", "--feature-set", type=str,
                        help='Name of the feature set used for prediction.')


def find_snippets_files(path: Path) -> List[Path]:
    paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            paths.append(Path(os.path.join(root, file)))
    return paths


def create_export_row(
        method: str,
        method_name: str,
        filepath: str,
        rc: ReadabilityCalculator
) -> Dict[str, Any]:
    _, readability = rc.compute_readability(method)
    return {
        CSV_COLUMNS[0]: filepath,
        CSV_COLUMNS[1]: method_name,
        CSV_COLUMNS[2]: readability,
    }


def create_export_rows(
        paths: List[Path],
        input_path: Path,
        rc: ReadabilityCalculator,
) -> Generator[Dict[str, Any], None, None]:
    for i, path in enumerate(paths):
        print(f'Progress: {i + 1} / {len(paths)}')
        print(str(path))

        with path.open() as f:
            source_code = f.read()

        # Use a naive way to get method name. Doesn't work in case that method name spans 2 rows.
        method_name = next(iter(source_code.splitlines()), '')
        yield create_export_row(source_code, method_name, str(path.relative_to(input_path)), rc)


def run(args: argparse.Namespace):
    input_path = args.input.resolve().absolute()
    output_path = args.output.resolve().absolute()
    model_name = args.model
    feature_set = args.feature_set or 'default'

    assert input_path.exists(), 'input path does not exist'
    assert model_name in utils.MODELS, 'model should be one of ' + str(list(utils.MODELS.keys()))
    assert feature_set in utils.MODELS[model_name], f'Model {model_name} does not support feature set {feature_set}'

    model_path = utils.MODELS[model_name][feature_set]

    rc = PickleReadabilityCalculator(
        model_path,
        language='cpp',
    )

    if input_path.is_file():
        paths = [input_path]
    else:
        paths = find_snippets_files(input_path)

    utils.export_csv(output_path, create_export_rows(paths, input_path, rc), headers=CSV_COLUMNS)

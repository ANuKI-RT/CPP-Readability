import argparse
from pathlib import Path
from typing import Generator, Dict, Any

import crawl_cmd
import utils
from cli_cmd import Command
from code_processing.parser import ClangParser
from readability.readability_calculator import ReadabilityCalculator, PickleReadabilityCalculator
from readability_cmd import create_export_row, CSV_COLUMNS


def register_command(subparsers):
    parser = subparsers.add_parser(
        str(Command.EXTRACT_READABILITY),
        description='Extract C++ methods and compute the readability in a given directory',
    )
    parser.add_argument("-i", "--input", type=Path, required=True,
                        help='Path to a directory contains C++ code snippets')
    parser.add_argument("-o", "--output", type=Path, default=Path('output.csv'),
                        help='Path to output csv file. Default is "output.csv".')
    parser.add_argument("-m", "--model", type=str, default='space_merged',
                        help='Name of the model (dataset name that model trained on). Default is "space_merged".')
    parser.add_argument("-fs", "--feature-set", type=str, default='posnett',
                        help='Name of the feature set used for prediction. Default is "posnett".')
    parser.add_argument("-gf", "--genFileKeyword", type=str, default='SampleKeyword',
                        help='If the cpp file contains this keyword it is (partly auto-generated)')
    parser.add_argument("-gm", "--genMethodKeyword", type=str, default='SampleKeyword2',
                        help='If the method does NOT contain this keyword AND '
                             'is part of a (partly) auto-generated cpp-file, the method is auto-generated --> skip it')


def create_export_rows(
        input_path: Path,
        rc: ReadabilityCalculator,
        gen_file_keyword: str,
        gen_method_keyword: str,
) -> Generator[Dict[str, Any], None, None]:
    cpp_files = crawl_cmd.find_cpp_files(input_path)
    clang_args = ['-x', 'c++', f'-I{str(input_path)}']
    parser = ClangParser(clang_args)

    extracted_signatures = set()

    for cpp_file in cpp_files:
        print(cpp_file)
        with cpp_file.open() as f:
            source_code = f.read()

        source_code = crawl_cmd.sanitize_file(source_code)
        is_generated_file = gen_file_keyword in source_code

        parser.parsing(source_code)
        methods = parser.extract_methods()

        for method in methods:
            method_lines = method.content.splitlines()
            signature = method_lines[0]

            if signature in extracted_signatures:
                continue
            if is_generated_file and (gen_method_keyword not in method.content):
                continue
            elif len(method_lines) < 10 or len(method_lines) > 50:
                continue

            extracted_signatures.add(signature)

            yield create_export_row(method.content, method.name, str(cpp_file.relative_to(input_path)), rc)


def run(args: argparse.Namespace):
    input_path = args.input.resolve().absolute()
    output_path = args.output.resolve().absolute()
    model_name = args.model
    feature_set = args.feature_set or 'default'

    assert args.input.is_dir(), 'input path should be a directory contains C++ code snippets'
    assert model_name in utils.MODELS, 'model should be one of ' + str(list(utils.MODELS.keys()))
    assert feature_set in utils.MODELS[model_name], f'Model {model_name} does not support feature set {feature_set}'

    model_path = utils.MODELS[model_name][feature_set]
    gen_file_keyword = args.genFileKeyword
    gen_method_keyword = args.genMethodKeyword

    rc = PickleReadabilityCalculator(
        model_path,
        language='cpp',
    )

    utils.export_csv(
        output_path,
        create_export_rows(input_path, rc, gen_file_keyword, gen_method_keyword),
        headers=CSV_COLUMNS,
    )

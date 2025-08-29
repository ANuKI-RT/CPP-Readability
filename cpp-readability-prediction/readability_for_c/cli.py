import argparse

import crawl_cmd
import extract_readability_cmd
import metrics_cmd
import readability_cmd
from cli_cmd import Command

command_executors = {
    str(Command.CRAWL): crawl_cmd,
    str(Command.METRICS): metrics_cmd,
    str(Command.READABILITY): readability_cmd,
    str(Command.EXTRACT_READABILITY): extract_readability_cmd,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='readability-for-c',
        description='A tool for extracting features and calculating readability of C++ code snippets',
    )
    subparser = parser.add_subparsers(
        dest='command',
        title='Commands',
        description=f'Could be one of: {", ".join(command_executors.keys())}',
        required=True,
    )
    for executor in command_executors.values():
        if executor is not None:
            executor.register_command(subparser)
    return parser.parse_args()


def run_cli():
    args = _parse_args()
    assert args.command in command_executors, f'Not supported command: {args.command}'
    command_executors[args.command].run(args)


if __name__ == '__main__':
    run_cli()

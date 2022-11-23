import argparse

from tangle.tangle import FileInterpreter


def create_args_parser():
    parser = argparse.ArgumentParser(
        prog="tangle",
        description="Copies markdown code blocks with the correct header syntax to target files.",
        usage="%(prog)s [options] <file>",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("file", type=str, help="a markdown file")

    return parser


class Cli:
    _args: argparse.Namespace

    def _eval_file(self) -> None:
        interpreter = FileInterpreter(self._args.file)

        interpreter.eval()

    def _parse_args(self) -> None:
        args_parser = create_args_parser()

        self._args = args_parser.parse_args()

    def run(self) -> None:
        self._parse_args()
        self._eval_file()

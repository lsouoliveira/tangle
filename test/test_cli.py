from argparse import Namespace
from os.path import samefile
from unittest.mock import patch
from tempfile import NamedTemporaryFile
import pytest

from tangle.cli import Cli


class TestCli:
    def create_sample(self, bashrc_path, alacritty_path):
        sample = open("sample/dotfile.md", "r").read()

        sample = sample.replace("[[BASHRC_PATH]]", bashrc_path)
        sample = sample.replace("[[ALACRITTY_PATH]]", alacritty_path)

        return sample

    def test_run(self):
        with NamedTemporaryFile("r") as bashrc_file:
            with NamedTemporaryFile("r") as alacritty_file:
                with NamedTemporaryFile("w+") as sample_file:
                    with patch(
                        "argparse.ArgumentParser.parse_args",
                        return_value=Namespace(file=sample_file.name),
                    ):
                        sample = self.create_sample(
                            bashrc_file.name, alacritty_file.name
                        )

                        sample_file.write(sample)
                        sample_file.seek(0)

                        cli = Cli()

                        cli.run()

                        assert (
                            bashrc_file.read() == open("sample/bashrc.sh", "r").read()
                        )
                        assert (
                            alacritty_file.read()
                            == open("sample/alacritty.yml", "r").read()
                        )

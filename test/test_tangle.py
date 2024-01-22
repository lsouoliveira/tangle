import os
from unittest.mock import MagicMock, mock_open, patch
import pytest
import tempfile

from tangle.parser import (
    CodeBlockNode,
    DocumentNode,
    StringParser,
    TextNode,
    UnaryOperatorNode,
    LinkNode,
)
from tangle.tangle import (
    BaseInterpreter,
    FileInterpreter,
    EvalVisitor,
    FilePath,
    write_to_file,
)


def create_document(dir):
    return DocumentNode(
        [
            CodeBlockNode(
                TextNode("ruby"),
                TextNode("puts 'Hello World'"),
                UnaryOperatorNode(">", TextNode(os.path.join(dir, "randomfile.rb"))),
            )
        ],
        [
            LinkNode(
                text=TextNode("link"),
                path=TextNode(os.path.join(dir, "randomfile.md")),
            )
        ],
    )


def create_randomfile_content(dir, filename="randomfile.rb"):
    content = "```ruby > {}/{}\nputs 'Hello World'\n```"

    return content.format(dir, filename)


def create_randomfile_content_with_link(dir):
    content = "- [randomfile2](randomfile2.md)\n```ruby > {}/randomfile.rb\nputs 'Hello World'\n```"

    return content.format(dir)


def test_write_to_file():
    path = os.path.expanduser("~/randomfile.txt")
    dirname = os.path.dirname(path)

    with patch("builtins.open", new_callable=mock_open()) as m:
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs") as makedir:
                write_to_file("content", path)

                m.assert_called_with(path, "w+")
                makedir.assert_called_with(dirname)


class TestEvalVisitor:
    def test_visit_document(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            visitor = EvalVisitor(FilePath(os.path.join(tmpdirname, "randomfile.md")))
            document = create_document(tmpdirname)

            with open(os.path.join(tmpdirname, "randomfile.md"), "w+") as f:
                f.write(create_randomfile_content(tmpdirname, "randomfile2.rb"))

            visitor.visit_document(document)

            with open(os.path.join(tmpdirname, "randomfile.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'"

            with open(os.path.join(tmpdirname, "randomfile2.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'\n"

    def test_visit_document_with_relative_path(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            visitor = EvalVisitor(FilePath(os.path.join(tmpdirname, "randomfile.md")))
            document = create_document("")

            with open(os.path.join(tmpdirname, "randomfile.md"), "w+") as f:
                f.write(create_randomfile_content(tmpdirname, "randomfile2.rb"))

            visitor.visit_document(document)

            with open(os.path.join(tmpdirname, "randomfile.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'"

            with open(os.path.join(tmpdirname, "randomfile2.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'\n"


class TestFilePath:
    def test_init_raises_error_with_empty_string(self):
        with pytest.raises(ValueError):
            FilePath("")

    def test_expanded(self):
        file_path = FilePath("~/randomfile")

        assert file_path.expanded() == os.path.expanduser("~/randomfile")

    def test_file_or_dir_exists(self):
        with patch("os.path.exists", return_value=False):
            file_path = FilePath("~/randomfile")

            assert file_path.file_or_dir_exists() == False

    def test_dirname(self):
        file_path = FilePath("~/randomfile")

        assert file_path.dirname() == os.path.dirname(
            os.path.expanduser("~/randomfile")
        )


class TestBaseInterpreter:
    def test_eval(self):
        parser = StringParser("")
        visitor = EvalVisitor(FilePath("~/randomfile"))
        document = DocumentNode()

        parser.parse = MagicMock(return_value=document)
        document.accept = MagicMock()

        interpreter = BaseInterpreter(parser, visitor)

        interpreter.eval()

        parser.parse.assert_called
        document.accept.assert_called_with(visitor)


class TestFileInterpreter:
    def test_eval(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            interpreter = FileInterpreter(
                os.path.join(tmpdirname, "randomfile.md"),
            )

            with open(os.path.join(tmpdirname, "randomfile.md"), "w+") as f:
                f.write(create_randomfile_content_with_link(tmpdirname))

            with open(os.path.join(tmpdirname, "randomfile2.md"), "w+") as f:
                f.write(create_randomfile_content(tmpdirname, "randomfile2.rb"))

            interpreter.eval()

            with open(os.path.join(tmpdirname, "randomfile.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'\n"

            with open(os.path.join(tmpdirname, "randomfile2.rb"), "r") as f:
                assert f.read() == "puts 'Hello World'\n"

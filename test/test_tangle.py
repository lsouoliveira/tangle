import os
from unittest.mock import MagicMock, mock_open, patch
import pytest

from tangle.parser import (
    CodeBlockNode,
    DocumentNode,
    StringParser,
    TextNode,
    UnaryOperatorNode,
)
from tangle.tangle import (
    BaseInterpreter,
    FileInterpreter,
    EvalVisitor,
    FilePath,
    write_to_file,
)


def test_write_to_file():
    path = "~/randomfile.txt"
    dirname = os.path.dirname(os.path.expanduser(path))

    with patch("builtins.open", new_callable=mock_open()) as m:
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs") as makedir:
                write_to_file("content", path)

                m.assert_called_with(path, "w")
                makedir.assert_called_with(dirname)


class TestEvalVisitor:
    @pytest.fixture
    def document(self):
        return DocumentNode(
            [
                CodeBlockNode(
                    TextNode("ruby"),
                    TextNode("content\ncontent\ncontent"),
                    UnaryOperatorNode(">", TextNode("~/randomfile.txt")),
                )
            ]
        )

    def test_visit_document(self, document):
        visitor = EvalVisitor()

        for i in range(document.count()):
            document.get(i).accept = MagicMock()

        document.accept(visitor)

        for i in range(document.count()):
            assert document.get(i).accept.called

    def test_visit_code_block(self, document):
        visitor = EvalVisitor()

        with patch("builtins.open", new_callable=mock_open()) as m:
            document.get(0).accept(visitor)

            m.assert_called_with("~/randomfile.txt", "w")


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
        visitor = EvalVisitor()
        document = DocumentNode()

        parser.parse = MagicMock(return_value=document)
        document.accept = MagicMock()

        interpreter = BaseInterpreter(parser, visitor)

        interpreter.eval()

        parser.parse.assert_called
        document.accept.assert_called_with(visitor)


class TestFileInterpreter:
    @patch("tangle.tangle.BaseInterpreter")
    def test_eval(self, base_interpreter_stub):
        with patch("builtins.open", new_callable=mock_open()) as m:
            interpreter = FileInterpreter("~/.randomfile")

            base_interpreter_stub.eval = MagicMock()

            interpreter.eval()

            m.assert_called_with("~/.randomfile", "r")
            base_interpreter_stub.assert_called

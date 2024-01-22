from __future__ import annotations

import abc
import os
from typing import cast

from tangle.parser import (
    DocumentNode,
    CodeBlockNode,
    Parser,
    StringParser,
    TextNode,
    Visitor,
)


def write_to_file(content: str, file_path: str) -> None:
    fpath = FilePath(file_path)

    if not fpath.file_or_dir_exists():
        os.makedirs(fpath.dirname())

    with open(fpath.expanded(), "w+") as f:
        f.write(content)


class Command(abc.ABC):
    @abc.abstractmethod
    def execute(self) -> None:
        raise NotImplementedError


class CopyToFileCommand(Command):
    _file_path: FilePath
    _content: str

    def __init__(self, file_path: FilePath, content: str):
        self._file_path = file_path
        self._content = content

    def execute(self) -> None:
        write_to_file(self._content, self._file_path.expanded())


class InterpretFileCommand(Command):
    file_path: FilePath

    def __init__(self, file_path: FilePath):
        self.file_path = file_path

    def execute(self) -> None:
        if not self.file_path.file_or_dir_exists():
            return

        if not self.file_path.isfile():
            return

        if not self.file_path.extension() == "md":
            return

        interpreter = FileInterpreter(self.file_path.expanded())
        interpreter.eval()


class FilePath:
    _path: str

    def __init__(self, path: str):
        if not path:
            raise ValueError("Path cannot be empty")

        self._path = path

    @property
    def path(self):
        return self._path

    def file_or_dir_exists(self) -> bool:
        dir_exists = not self.dirname() or os.path.exists(self.dirname())

        return os.path.exists(self._path) or dir_exists

    def isdir(self) -> bool:
        return os.path.isdir(self.expanded())

    def isfile(self) -> bool:
        return os.path.isfile(self.expanded())

    def isabs(self) -> bool:
        return os.path.isabs(self.expanded())

    def expanded(self) -> str:
        return os.path.expanduser(self._path)

    def dirname(self) -> str:
        return os.path.dirname(self.expanded())

    def extension(self) -> str:
        components = self._path.split(".")

        if len(components) <= 1:
            return ""

        return components[-1]

    def __eq__(self, o: "FilePath") -> bool:
        return self._path == o.path

    def __repr__(self):
        return self._path

    def __str__(self):
        return self._path

    def __unicode__(self):
        return self._path


class EvalVisitor(Visitor):
    def __init__(self, root_path: FilePath):
        self._root_path = root_path

    def visit_document(self, document: DocumentNode) -> None:
        for i in range(document.count()):
            document.get(i).accept(self)

        for link in document.links:
            file_path = self._file_path(link.path.value)

            command = InterpretFileCommand(file_path)
            command.execute()

    def visit_code_block(self, code_block: CodeBlockNode) -> None:
        operator = code_block.operator

        if operator.operator == ">":
            text_node = cast(TextNode, operator.operand)
            file_path = self._file_path(text_node.value)
            content = code_block.content.value

            command = CopyToFileCommand(file_path, content)
            command.execute()

    def visit_unary_operator(self, _) -> None:
        pass

    def visit_text(self, _) -> None:
        pass

    def _file_path(self, path: str) -> FilePath:
        if os.path.isabs(path):
            return FilePath(path)

        return FilePath(os.path.join(self._root_path.dirname(), path))


class Interpreter(abc.ABC):
    @abc.abstractmethod
    def eval(self) -> None:
        raise NotImplementedError


class BaseInterpreter(Interpreter):
    _parser: Parser
    _visitor: Visitor
    _document: DocumentNode

    def __init__(self, parser: Parser, visitor: Visitor):
        self._parser = parser
        self._visitor = visitor
        self._document = DocumentNode()

    def __parse(self):
        self._document = self._parser.parse()

    def __evaluate(self):
        self._document.accept(self._visitor)

    def __clear(self):
        self._document = DocumentNode()

    def eval(self) -> None:
        self.__parse()
        self.__evaluate()
        self.__clear()


class FileInterpreter(Interpreter):
    _path: FilePath
    _format: str
    _parser: Parser

    def __init__(self, path: str, format="plaintext"):
        if format not in ["plaintext"]:
            raise ValueError("Format {} is not supported".format(format))

        self._path = FilePath(path)
        self._format = format

    def __create_parser(self):
        if self._format == "plaintext":
            with open(self._path.expanded(), "r") as f:
                self._parser = StringParser(f.read())

    def __evaluate(self) -> None:
        base_interpreter = BaseInterpreter(self._parser, EvalVisitor(self._path))

        base_interpreter.eval()

    def eval(self) -> None:
        self.__create_parser()
        self.__evaluate()

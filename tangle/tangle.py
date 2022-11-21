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
    _code_block: CodeBlockNode

    def __init__(self, code_block: CodeBlockNode):
        self._code_block = code_block

    def execute(self) -> None:
        write_to_file(self.__content(), self.__file_path())

    def __file_path(self) -> str:
        operator = self._code_block.operator
        operand = cast(TextNode, operator.operand)

        return operand.value

    def __content(self) -> str:
        return self._code_block.content.value


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

    def expanded(self) -> str:
        return os.path.expanduser(self._path)

    def dirname(self) -> str:
        return os.path.dirname(self.expanded())

    def __eq__(self, o: "FilePath") -> bool:
        return self._path == o.path

    def __repr__(self):
        return self._path

    def __str__(self):
        return self._path

    def __unicode__(self):
        return self._path


class EvalVisitor(Visitor):
    def visit_document(self, document: DocumentNode) -> None:
        for i in range(document.count()):
            document.get(i).accept(self)

    def visit_code_block(self, code_block: CodeBlockNode) -> None:
        operator = code_block.operator

        if operator.operator == ">":
            command = CopyToFileCommand(code_block)

            command.execute()

    def visit_unary_operator(self, _) -> None:
        pass

    def visit_text(self, _) -> None:
        pass


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
    _path: str
    _format: str
    _parser: Parser

    def __init__(self, path: str, format="plaintext"):
        if not format in ["plaintext"]:
            raise ValueError("Format {} is not supported".format(format))

        self._path = path
        self._format = format

    def __create_parser(self):
        if self._format == "plaintext":
            with open(self._path, "r") as f:
                self._parser = StringParser(f.read())

    def __evaluate(self) -> None:
        base_interpreter = BaseInterpreter(self._parser, EvalVisitor())

        base_interpreter.eval()

    def eval(self) -> None:
        self.__create_parser()
        self.__evaluate()

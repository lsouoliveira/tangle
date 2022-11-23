from enum import Enum, auto
from typing import List, Tuple
import abc
import re

OPERATORS = [">"]


def is_operator(s: str) -> bool:
    return s in OPERATORS


def split_code_block_header_components(
    source: str,
) -> Tuple[str | None, str | None, str | None]:
    components = source.split()

    if len(components) <= 1 or (len(components) <= 2 and components[1] in OPERATORS):
        return None, None, None

    if is_operator(components[0]):
        return None, components[0], components[1]

    if is_operator(components[1]):
        return components[0], components[1], components[2]

    return None, None, None


class AstNodeType(Enum):
    DOCUMENT = auto()
    CODE_BLOCK = auto()
    UNARY_OPERATOR_NODE = auto()
    TEXT_NODE = auto()


class AstNode:
    _node_type: AstNodeType

    def __init__(self, node_type):
        self._node_type = node_type

    def node_type(self):
        return self._node_type

    @abc.abstractmethod
    def accept(self, visitor) -> None:
        raise NotImplementedError


class DocumentNode(AstNode):
    _blocks: List[AstNode]

    def __init__(self, blocks: List[AstNode] | None = None):
        super().__init__(AstNodeType.DOCUMENT)

        self._blocks = blocks or []

    def add(self, node: AstNode) -> None:
        self._blocks.append(node)

    def get(self, index: int) -> AstNode:
        return self._blocks[index]

    def count(self) -> int:
        return len(self._blocks)

    def accept(self, visitor) -> None:
        visitor.visit_document(self)


class UnaryOperatorNode(AstNode):
    operator: str
    operand: AstNode

    def __init__(self, operator: str, operand: AstNode):
        super().__init__(AstNodeType.UNARY_OPERATOR_NODE)

        self.operator = operator
        self.operand = operand

    def accept(self, visitor) -> None:
        visitor.visit_unary_operator(self)


class TextNode(AstNode):
    value: str

    def __init__(self, value=""):
        super().__init__(AstNodeType.TEXT_NODE)

        self.value = value

    def accept(self, visitor) -> None:
        visitor.visit_text(self)


class CodeBlockNode(AstNode):
    info: TextNode
    content: TextNode
    operator: UnaryOperatorNode

    def __init__(self, info: TextNode, content: TextNode, operator: UnaryOperatorNode):
        super().__init__(AstNodeType.CODE_BLOCK)

        self.info = info
        self.content = content
        self.operator = operator

    def accept(self, visitor) -> None:
        visitor.visit_code_block(self)


class Parser(abc.ABC):
    @abc.abstractmethod
    def parse(self) -> DocumentNode:
        raise NotImplementedError


class StringParser(Parser):
    _source: str
    _code_block_pattern: re.Pattern

    def __init__(self, source: str):
        self._source = source
        self._code_block_pattern = re.compile(
            "(```.*?\n[.*?\n]?```$)", flags=re.DOTALL | re.MULTILINE
        )

    def __parse_code_block(self, source: str) -> CodeBlockNode | None:
        lines = source.splitlines()
        header = lines[0][3:]

        info, operator, path = split_code_block_header_components(header)

        content = "\n".join(lines[1:-1]) + "\n"

        if not operator or not path:
            return None

        return CodeBlockNode(
            TextNode(info or ""),
            TextNode(content),
            UnaryOperatorNode(operator, TextNode(path)),
        )

    def __code_block_matches(self):
        return self._code_block_pattern.findall(self._source)

    def parse(self) -> DocumentNode:
        document = DocumentNode()

        for match in self.__code_block_matches():
            block = self.__parse_code_block(match)

            if block:
                document.add(block)

        return document


class Visitor(abc.ABC):
    @abc.abstractmethod
    def visit_document(self, document: DocumentNode) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_code_block(self, code_block: CodeBlockNode) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unary_operator(self, unary_operator: UnaryOperatorNode) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_text(self, text: TextNode) -> None:
        raise NotImplementedError

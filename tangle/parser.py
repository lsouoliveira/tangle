from enum import Enum, auto
from typing import List, Tuple, cast
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
    BINARY_OPERATOR_NODE = auto()
    TEXT_NODE = auto()


class AstNode:
    _node_type: AstNodeType

    def __init__(self, node_type):
        self._node_type = node_type

    def node_type(self):
        return self._node_type


class DocumentNode(AstNode):
    _blocks: List[AstNode]

    def __init__(self):
        super().__init__(AstNodeType.DOCUMENT)

        self._blocks = []

    def add(self, node: AstNode) -> None:
        self._blocks.append(node)

    def get(self, index: int) -> AstNode:
        return self._blocks[index]

    def count(self) -> int:
        return len(self._blocks)


class BinaryOperatorNode(AstNode):
    operator: str
    operand1: AstNode
    operand2: AstNode

    def __init__(self, operator: str, operand1: AstNode, operand2: AstNode):
        super().__init__(AstNodeType.BINARY_OPERATOR_NODE)

        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2


class TextNode(AstNode):
    content: str

    def __init__(self, content=""):
        super().__init__(AstNodeType.TEXT_NODE)

        self.content = content


class CodeBlockNode(AstNode):
    info: TextNode
    content: TextNode
    operator: BinaryOperatorNode

    def __init__(self, info: TextNode, content: TextNode, operator: BinaryOperatorNode):
        super().__init__(AstNodeType.CODE_BLOCK)

        self.info = info
        self.content = content
        self.operator = operator


class Parser(abc.ABC):
    @abc.abstractmethod
    def parse(self) -> DocumentNode:
        raise NotImplementedError


class StringParser(abc.ABC):
    _source: str
    _code_block_pattern: re.Pattern

    def __init__(self, source: str):
        self._source = source
        self._code_block_pattern = re.compile(
            "(```.*?\n[.*?\n]?```$)", flags=re.DOTALL | re.MULTILINE
        )

    def __parse_binary_operator(self, source) -> BinaryOperatorNode | None:
        info, operator, path = split_code_block_header_components(source)

        if not operator or not path:
            return None

        return BinaryOperatorNode(operator, TextNode(info or ""), TextNode(path))

    def __parse_code_block(self, source: str) -> CodeBlockNode | None:
        lines = source.splitlines()

        binary_operator_node = self.__parse_binary_operator(lines[0][3:])
        content = "\n".join(lines[1:-1])

        if not binary_operator_node:
            return None

        return CodeBlockNode(
            cast(TextNode, binary_operator_node.operand1),
            TextNode(content),
            binary_operator_node,
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

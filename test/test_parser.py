import pytest
from typing import cast
from tangle.parser import (
    AstNodeType,
    UnaryOperatorNode,
    CodeBlockNode,
    DocumentNode,
    StringParser,
    TextNode,
)


def test_document_node():
    assert DocumentNode().node_type() == AstNodeType.DOCUMENT


def test_binary_operator_node():
    node = UnaryOperatorNode(">", TextNode()).node_type()

    assert node == AstNodeType.UNARY_OPERATOR_NODE


def test_text_node():
    assert TextNode().node_type() == AstNodeType.TEXT_NODE


def test_code_block_node():
    node = CodeBlockNode(
        TextNode(), TextNode(), UnaryOperatorNode(">", TextNode())
    ).node_type()

    assert node == AstNodeType.CODE_BLOCK


class TestStringParser:
    @pytest.fixture
    def document_with_code_block(self):
        return "```ruby > ~/animal.rb\nclass Animal\nend\n```"

    @pytest.fixture
    def documents_with_missing_params(self):
        return ["```ruby >\n\n```", "```ruby ~/.animal\n\n```"]

    @pytest.fixture
    def document_with_code_block_without_info_string(self):
        return "```> ~/animal.rb\nclass Animal\nend\n```"

    @pytest.fixture
    def document_with_multiple_code_blocks(self):
        return "``` > ~/path\ncontent```\n```\n\n```\n```ruby > ~/animal.rb\nclass Animal\nend\n```\n\n```ruby > ~/animal.rb\nclass Animal\nend\n```"

    @pytest.fixture
    def ruby_class(self):
        return "class Animal\nend"

    def test_parser_returns_empty_document(self):
        parser = StringParser("")

        node = parser.parse()

        assert node.node_type() == AstNodeType.DOCUMENT
        assert node.count() == 0

    def test_parser_parse_code_block(self, document_with_code_block, ruby_class):
        parser = StringParser(document_with_code_block)

        node = parser.parse()

        assert node.count() == 1

        code_block = cast(CodeBlockNode, node.get(0))
        block_info_text = cast(TextNode, code_block.info)
        block_content = cast(TextNode, code_block.content)

        block_operator = cast(UnaryOperatorNode, code_block.operator)
        block_operator_operand = cast(TextNode, block_operator.operand)

        assert code_block.node_type() == AstNodeType.CODE_BLOCK
        assert block_info_text.content == "ruby"
        assert block_content.content == ruby_class

        assert block_operator_operand.content == "~/animal.rb"

    def test_parser_parse_code_block_without_info_string(
        self, document_with_code_block_without_info_string, ruby_class
    ):
        parser = StringParser(document_with_code_block_without_info_string)

        node = parser.parse()

        assert node.count() == 1

        code_block = cast(CodeBlockNode, node.get(0))
        block_info_text = cast(TextNode, code_block.info)
        block_content = cast(TextNode, code_block.content)

        block_operator = cast(UnaryOperatorNode, code_block.operator)
        block_operator_operand = cast(TextNode, block_operator.operand)

        assert code_block.node_type() == AstNodeType.CODE_BLOCK
        assert block_info_text.content == ""
        assert block_content.content == ruby_class

        assert block_operator_operand.content == "~/animal.rb"

    def test_parser_doesnt_parse_with_missing_params(
        self, documents_with_missing_params
    ):
        for document_with_missing_params in documents_with_missing_params:
            parser = StringParser(document_with_missing_params)

            node = parser.parse()

            assert node.count() == 0

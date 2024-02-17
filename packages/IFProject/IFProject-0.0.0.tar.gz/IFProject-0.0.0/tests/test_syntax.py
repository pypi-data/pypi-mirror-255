from engine.syntax import (
    A,
    Expression,
    If,
    Node,
    Sequence,
    Variable,
    empty_syntax,
    simple_syntax,
    syntax_v1,
)
from pytest import fixture

# Test Basic Nodes ------------------------------------------------------------


# Node
@fixture
def example_node():
    return Node()


def test_type_property(example_node):
    assert example_node.type == "Node"


# Expression --------------------------------------------------------------


@fixture
def example_expression():
    return Expression(data="test")


def test_initialization(example_expression):
    assert example_expression.data == "test"
    assert example_expression.pattern == ".*"


# Sequence
def test_empty_sequence():
    empty_sequence = Sequence([])
    assert empty_sequence.data == []


# Map ---------------------------------------------------------------------


@fixture
def example_map():
    return A(data={"a": Expression(data="test")})


def test_get_item(example_map):
    assert example_map["a"] == Expression(data="test")


# Simple Syntax ------------------------------------------------------------


def test_empty_syntax():
    assert not empty_syntax.expressions
    assert not empty_syntax.sequences
    assert not empty_syntax.maps


def test_simple_syntax_extension():
    assert If in simple_syntax.types
    assert A in simple_syntax.types


# Variable -----------------------------------------------------------------


def test_pattern():
    var = Variable(data="var")
    assert var.pattern == "^[a-zA-Z_][a-zA-Z0-9_]*$"


# Syntax V1
def test_v1_syntax_extension():
    assert Variable in syntax_v1.types

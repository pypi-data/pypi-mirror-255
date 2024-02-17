import pytest
from engine.parser import Parser
from engine.syntax import A, Expression, If, Node, Sequence


class MyTestCase:
    val: str
    expected: Node


@pytest.fixture
def test_cases():
    class a_obj(MyTestCase):
        val = "a: action"
        expects = A(data={"a": Expression(data="action")})

    class if_obj(MyTestCase):
        val = """
    if: condition1
    then:
    - a: action1
    else:
    - a: action2
    """
        expects = If(
            {
                "if": Expression(data="condition1"),
                "then": Sequence(
                    [
                        A(data={"a": Expression(data="action1")}),
                    ]
                ),
                "else": Sequence(
                    [
                        A(data={"a": Expression(data="action2")}),
                    ]
                ),
            }
        )

    return [a_obj, if_obj]


@pytest.fixture
def parser():
    return Parser()


def test_parse(test_cases, parser):
    for case in test_cases:
        node = parser.parse(case.val)
        assert node == case.expects


def test_dump(test_cases, parser):
    for case in test_cases:
        yaml = parser.dump(case.expects)
        node = parser.parse(yaml)

        assert node == case.expects

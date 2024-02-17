"""Test Stories

+--------------------------+--------------------------------+
| Story                    | Description                    |
+--------------------------+--------------------------------+
| hello_world              | tests PRINT                    |
| error                    | tests ERROR                    |
| simple_choice            | tests CHOICE                   |
| simple_goto              | tests GOTO                     |
| simple_choice_goto       | tests CHOICE and GOTO together |
| simple_vars              | tests Vars and IF              |
| default_var_values       | tests Vars and IF              |
| simple_gosub             | tests GOSUB                    |
+--------------------------+--------------------------------+


TODO: One for erroneous stories to test "error handling" without a complete crash
"""

import logging
from pathlib import Path

import pytest
from engine.parser import dump, parse

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "story",
    Path().glob("tests/stories/*.yaml"),
)
def test_parse_stories(story):
    log.info(f"Parsing story: {str(story)}")
    ast_1 = parse(story)
    ast_2 = parse(dump(ast_1))
    assert ast_1 == ast_2

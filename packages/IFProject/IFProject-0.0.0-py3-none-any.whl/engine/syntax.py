import types
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

# Base Nodes ------------------------------------------------------------------


class Node:
    @property
    def type(self):
        return self.__class__.__name__


NodeType = type[Node]
NodeTypes = tuple[NodeType]


class NodeRef:
    name: str
    ...


class ExpressionRef(NodeRef):
    ...


class SequenceRef(NodeRef):
    ...


class MapRef(NodeRef):
    name: str
    type: str


@dataclass
class Expression(Node):
    data: str
    pattern: str = ".*"


ExpressionType = type[Expression]
ExpressionTypes = tuple[ExpressionType]


@dataclass
class Sequence(Node):
    data: list


SequenceType = type[Sequence]
SequenceTypes = tuple[SequenceType]


@dataclass
class Tag:
    key: str
    type: Node
    optional: bool = False


Tags = list[Tag]


@dataclass
class Map(Node):
    data: dict
    spec: Tags

    def __getitem__(self, key: str) -> Any:
        return self.data[key]


MapType = type[Map]
MapTypes = tuple[MapType]


# Syntax ----------------------------------------------------------------------


@dataclass
class Syntax:
    types: NodeTypes

    @property
    def expressions(self) -> ExpressionTypes:
        return self.by_type(Expression)

    @property
    def sequences(self) -> SequenceTypes:
        return self.by_type(Sequence)

    @property
    def maps(self) -> MapTypes:
        return self.by_type(Map)

    def by_type(self, target_type: NodeType) -> NodeTypes:
        return [t for t in self.types if issubclass(t, target_type)]

    def extend(self, *new_types: NodeTypes) -> "Syntax":
        return replace(self, types=self.types + list(new_types))


# Initial syntax --------------------------------------------------------------


empty_syntax = Syntax(types=[])

initial_syntax = Syntax(types=[Expression, Sequence])


# Basic Syntax ----------------------------------------------------------------


@dataclass
class A(Map):
    spec: Tags = (Tag("a", Expression),)


@dataclass
class If(Map):
    spec: Tags = (
        Tag("if", Expression),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


@dataclass
class Variable(Expression):
    pattern: str = "^[a-zA-Z_][a-zA-Z0-9_]*$"


simple_syntax = initial_syntax.extend(If, A, Variable)
syntax_v1 = simple_syntax


node_class_dict = {
    "A": A,
}

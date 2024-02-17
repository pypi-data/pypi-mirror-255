from pathlib import Path

import yaml

from engine.exceptions import NotRecognized
from engine.syntax import (
    Expression,
    Map,
    MapType,
    Node,
    NodeType,
    Sequence,
    Syntax,
    syntax_v1,
)

PoPo = str | list | dict


class Parser:
    """A Parser that can parse Yaml or PoPo into AST Nodes and back again.

    Public Methods:
        parse: Parse a YAML string or file into an AST Node.
        dump: Dump an AST Node into a YAML string.

    Private Methods:
        _parse: Parse a PoPo into an AST Node according to the given node_type.
        _parse_map: Parse a dictionary into a Map node.
        _dump: Dump an AST Node back into a PoPo.
    """

    def __init__(self, syntax: Syntax = syntax_v1):
        """Initialize the Parser with a given syntax.

        Args:
            syntax (Syntax, optional): The syntax to use when parsing.
                Defaults to syntax_v1.
        """
        self.syntax = syntax

    def parse(self, data: str | Path) -> Node:
        """Parse a YAML string or file into an AST Node.

        Args:
            data (str | Path): The YAML data string or file to parse.

        Returns:
            Node: An AST Node that represents the parsed YAML data.

        Raises:
            NotRecognized: If the data is not recognized.
        """
        if isinstance(data, Path):
            data = data.read_text()

        data = yaml.load(data, Loader=yaml.FullLoader)
        return self._parse(data, node_type=None)

    def dump(self, node: Node, file: Path = None) -> str:
        """Dump an AST Node into a YAML string.

        Args:
            node (Node): The AST Node to dump.
            file (Path, optional): The file to dump the YAML string to.

        Returns:
            str: A string that represents the YAML format of the AST Node.

        Effects:
            Writes the YAML string to the given file.
        """
        result = yaml.dump(self._dump(node))

        if file:
            file.write_text(result)

        return result

    def _parse(self, data: PoPo, node_type: NodeType) -> Node:
        # Hack to match node types with class patterns
        node_type_instance = node_type({}) if node_type else None

        match data, node_type_instance:
            case str(), Expression():
                return node_type(data)

            case list(), Sequence():
                return Sequence([self._parse(item, None) for item in data])

            case dict(), None | Map():
                return self._parse_map(data, node_type)

            case _:
                raise TypeError(f"Data: {data} does not match node {node_type}")

    def _parse_map(self, data, node_type: MapType | None) -> Map:
        candidate_nodes = [node_type] if node_type else self.syntax.maps
        for node in candidate_nodes:
            if all(tag.key in data or tag.optional for tag in node.spec):
                result = {
                    tag.key: self._parse(data[tag.key], tag.type)
                    for tag in node.spec
                    if tag.key in data
                }
                return node(result)
        raise NotRecognized(f"Unrecognized map: {data}")

    def _dump(self, node: Node) -> PoPo:
        match node:
            case Expression(data):
                return data
            case Map(data):
                return {k: self._dump(v) for k, v in data.items()}
            case Sequence(data):
                return [self._dump(item) for item in data]
            case Node():
                raise NotRecognized(f"Unrecognized node: {node}")
            case _:
                raise TypeError(f"Expected Node, got: {type(node)}")


# Publish the default parser
parser = Parser()
parse = parser.parse
dump = parser.dump

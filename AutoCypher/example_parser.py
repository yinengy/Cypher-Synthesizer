from pathlib import Path
from typing import List, Dict

from record import Node, Relation, Output

TYPE_OUTPUT = "output"
TYPE_NODE = "node"
TYPE_RELATION = "rel"
TYPE_CONSTANT = "constant"

class Example:
    """
    A I/O example of a graph query
    """
    nodes: Dict[str, List[Node]]
    relations: Dict[str, List[Relation]]
    output: List[Output]
    constants: List[str]

    def __init__(self, example_dir_path: str) -> None:
        self.nodes = {}
        self.relations = {}
        self.output = []
        self.constants = []

        self._parse_example(example_dir_path)

    def _parse_example(self, path) -> None:
        """
        Parse I/O example in diretory ```path```

        format of each file:
        <type>[,<label>]
        <property_name 1>,<property_name 2>...
        <value 1>,<value 2>...
        ...
        """
        path = Path(path)
        relation_files = []

        for f in [x for x in path.iterdir() if x.is_file()]:  # loop over all files
            with f.open() as ex:
                lines = [line.strip() for line in ex.readlines()]
                
                ex_type = lines[0].split(",")[0]

                if ex_type == TYPE_OUTPUT:
                    self._parse_output(lines[1:])
                elif ex_type == TYPE_NODE:
                    self._parse_nodes(lines[0].split(",")[1], lines[1:])
                elif ex_type == TYPE_RELATION:
                    # relation should be parsed at the end since it need to find previous node objects
                    relation_files.append(f)
                elif ex_type == TYPE_CONSTANT:
                    self.constants.extend(lines[1:])
                else:
                    raise RuntimeError(f"Illegall file: {f.absolute}")

        # parse relation
        for f in relation_files:
            with f.open() as ex:
                lines = [line.strip() for line in ex.readlines()]
                self._parse_relations(lines[0].split(",")[1], lines[1:])

    def _parse_nodes(self, label: str, lines: List[str]) -> None:
        """
        format:
        <property_name 1>,<property_name 2>...
        <value 1>,<value 2>...
        ...
        """
        property_name = lines[0].split(",")
        property_num = len(property_name)

        nodes = []
        for l in lines[1:]:
            values = l.split(",")
            
            node = Node(label, int(values[0]))
            for i in range(1, property_num):  
                node.properties[property_name[i]] = values[i]
            nodes.append(node)

        self.nodes[label] = nodes

    def _parse_relations(self, label: str, lines: List[str]) -> None:
        """
        format:
        id,<src_node Label>,<dst_node Label>[,<property name 1> ...]
        <int>,<node_id 1>,<node_id 2>[, <property value 1> ...]
        ...

        Note: the relation has direction from src to dst
        """
        first_line_split = lines[0].split(",")

        src_node_label = first_line_split[1]
        dst_node_label = first_line_split[2]
        property_name = first_line_split[3:]

        property_num = len(property_name)

        rels = []
        for l in lines[1:]:
            line_split = l.split(",")

            rel_id = int(line_split[0])
            src_node_id = int(line_split[1])
            dst_node_id = int(line_split[2])
            values = line_split[3:]

            # find node object by id and label
            src_node = self.nodes[src_node_label][src_node_id]
            dst_node = self.nodes[dst_node_label][dst_node_id]

            rel = Relation(label, src_node, dst_node, rel_id)
            for i in range(property_num):  
                rel.properties[property_name[i]] = values[i]
            rels.append(rel)

        self.relations[label] = rels

    def _parse_output(self, lines: List[str]) -> None:
        """
        format:
        <property_name 1>,<property_name 2>...
        <value 1>,<value 2>...
        ...
        """
        keys = lines[0].split(",")

        for l in lines[1:]:
            output = Output()
            output.keys = keys
            output.values = l.split(",")
            self.output.append(output)
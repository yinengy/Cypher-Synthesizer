
class Node:
    """
    A node in graph
    """
    def __init__(self, label: str, node_id: int) -> None:
        self.label = label
        self.id = node_id
        self.properties = {}

    def short_repr(self) -> str:
        return f"(:{self.label})"

    def __repr__(self) -> str:
        properties_str_list = [k + ": " + '"' + v + '"' for k, v in self.properties.items()]
        return f"<node {self.id} (:{self.label} {{{', '.join(properties_str_list)}}})>"

class Relation:
    """
    A relation between two nodes
    """
    def __init__(self, label: str, src_node: Node, dst_node: Node, rel_id: int) -> None:
        self.label = label
        self.id = rel_id
        self.src_node = src_node
        self.dst_node = dst_node
        self.properties = {}

    def __repr__(self) -> str:
        properties_str_list = [k + ": " + '"' + v + '"' for k, v in self.properties.items()]

        src_str = self.src_node.short_repr()
        dst_str = self.dst_node.short_repr()
        rel_str = f"-[:{self.label} {{{', '.join(properties_str_list)}}}]->"  # the direction is fixed
        return f"<rel {self.id} " + src_str + rel_str + dst_str + ">"

class Output:
    """
    An output of a query (a single row)
    """
    def __init__(self) -> None:
        self.properties = {}

    def __repr__(self) -> str:
        properties_str_list = [k + ": " + '"' + v + '"' for k, v in self.properties.items()]

        return f"Output {{{', '.join(properties_str_list)}}}"
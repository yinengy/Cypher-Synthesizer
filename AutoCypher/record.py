
class Node:
    """
    A node in graph
    """
    def __init__(self, label: str, node_id: int) -> None:
        self.label = label
        self.id = node_id
        self.properties = {}

    def short_repr(self) -> str:
        """
        (:label)
        """
        return f"(:{self.label})"

    def str_with_variable(self, variable: str) -> str:
        """
        (variable:label {property: 'value'})
        """
        properties_str_list = [k + ": " + '"' + v + '"' for k, v in self.properties.items()]
        return f"({variable}:{self.label} {{{', '.join(properties_str_list)}}})"

    def __str__(self) -> str:
        """
        (:label {property: 'value'})
        """
        return self.str_with_variable("")

    def __repr__(self) -> str:
        """
        <node id (:label {property: 'value'})>
        """
        return f"<node {self.id} {self.__str__()}>"


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

    def short_repr(self) -> str:
        """
        -[:label {property: 'value'}]->
        """
        return self.short_repr_with_variable("")

    def short_repr_with_variable(self, variable: str) -> str:
        """
        -[variable:label {property: 'value'}]->
        """
        properties_str_list = [k + ": " + '"' + v + '"' for k, v in self.properties.items()]
        rel_str = f"-[{variable}:{self.label} {{{', '.join(properties_str_list)}}}]->"  # the direction is fixed
        return rel_str

    def __str__(self) -> str:
        """
        (:node_label {property: 'value'})-[:label {property: 'value'}]->(:node_label2 {property: 'value'})
        """
        src_str = str(self.src_node)
        dst_str = str(self.dst_node)
        return src_str + self.short_repr() + dst_str

    def __repr__(self) -> str:
        """
        <rel id (:node_label {property: 'value'})-[:label {property: 'value'}]->(:node_label2 {property: 'value'})>
        """
        src_str = self.src_node.short_repr()
        dst_str = self.dst_node.short_repr()
        return f"<rel {self.id} " + src_str + self.short_repr() + dst_str + ">"

class Output:
    """
    An output of a query (a single row)
    """
    def __init__(self) -> None:
        self.keys = []
        self.values = []

    def __repr__(self) -> str:
        key_value_list = [k + ": " + '"' + v + '"' for k, v in zip(self.keys, self.values)]

        return f"Output {{{', '.join(key_value_list)}}}"
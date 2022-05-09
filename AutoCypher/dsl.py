from typing import List

class DSL:
    """
    A Domain Specific Language for AutoCypher.

    Input/Output will be synthesized to this DSL.
    After that, the DSL will be translated to Cypher query.
    """
    def __init__(self) -> None:
        pass


class Node(DSL):
    """
    Syntax:
    Node <variable> <label>

    Corresponding Cypher:
    (variable:label)
    """
    def __init__(self, label: str, variable: str) -> None:
        super().__init__()
        self.label = label
        self.variable = variable

    def __repr__(self) -> str:
        return f"<Node {self.variable} {self.label}>"


class Relation(DSL):
    """
    Syntax:
    Relation <variable> <label>

    Corresponding Cypher:
    -[variable:label]->
    """
    def __init__(self, label: str, variable: str) -> None:
        super().__init__()
        self.label = label
        self.variable = variable

    def __repr__(self) -> str:
        return f"<Rel {self.variable} {self.label}>"


class Match(DSL):
    """
    Syntax:
    Match <Node> [<Relation> <Node 2>]

    Corresponding Cypher:
    Match (Node)[-[Relation]->(Node 2)]
    """
    def __init__(self, node: Node, relation: Relation = None, node2: Node = None) -> None:
        super().__init__()
        self.node = node
        self.relation = relation
        self.node2 = node2

    def __repr__(self) -> str:
        if self.relation is not None:
            return f"<Match {self.node} {self.relation} {self.node2}>"
        else:
            return f"<Match {self.node}>"


class Return(DSL):
    """
    Syntax:
    Return <variable1> <value1> <varibale2> <value2> ...

    Corresponding Cypher:
    RETURN <variable1>.<value1>, <varibale2>.<value2>, ...
    """
    def __init__(self, values: List[str], variables: List[str]) -> None:
        super().__init__()
        self.values = values
        self.variables = variables

    def __repr__(self) -> str:
        tmp = [var + " " + val for var, val in zip(self.variables, self.values)]
        return f"<Return {' '.join(tmp)}>"

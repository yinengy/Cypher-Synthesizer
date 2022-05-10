from typing import List
from unittest.util import strclass
import abc

class DSL:
    """
    A Domain Specific Language for AutoCypher.

    Input/Output will be synthesized to this DSL.
    After that, the DSL will be translated to Cypher query.

    General Structure:
    <Match 1>
    <Match 2>
    ...
    <Require 1>
    <Require 2>
    ...
    <Return>
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_Cypher(self) -> str:
        raise NotImplementedError("Please Implement this method")


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

    def to_Cypher(self) -> str:
        return f"({self.variable}:{self.label})"


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

    def to_Cypher(self) -> str:
        return  f"-[{self.variable}:{self.label}]->"


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

    def to_Cypher(self) -> str:
        if self.relation is not None:
            return f"MATCH {self.node.to_Cypher()}{self.relation.to_Cypher()}{self.node2.to_Cypher()}"
        else:
            return f"MATCH {self.node.to_Cypher()}"


class Return(DSL):
    """
    Note: instead of directly translate to Cypher RETURN
    this DSL Return statement include a property exitence checking to speedup searching 

    Syntax:
    Return <variable1> <property1> <varibale2> <property2> ...

    Corresponding Cypher:
    WHERE <variable1>.<property1> IS NOT NULL AND ...
    RETURN <variable1>.<property1>, <varibale2>.<property2>, ...
    """
    def __init__(self, properties: List[str], variables: List[str]) -> None:
        super().__init__()
        self.properties= properties
        self.variables = variables

    def __repr__(self) -> str:
        tmp = [var + " " + val for var, val in zip(self.variables, self.properties)]
        return f"<Return {' '.join(tmp)}>"

    def to_Cypher(self) -> str:
        with_str = "WITH *"
        tmp = [var + "." + val for var, val in zip(self.variables, self.properties)]
        return_str = f"RETURN {', '.join(tmp)}"

        tmp2 = [s + " IS NOT NULL" for s in tmp]
        checking_str = f"WHERE {' AND '.join(tmp2)}"

        return with_str + '\n' + checking_str + '\n' + return_str

class Condition(DSL):
    """
    Condtions on properties
    e.g. compare two property
         one property equals to a constant
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_Cypher(self) -> str:
        raise NotImplementedError("Please Implement this method")

class EqualTo(Condition):
    """
    A property equals to a constant

    Syntax
    EqualTo <variable> <property> "<constant>"

    Corresponding Cypher:
    <variable>.<property> = "<constant>"
    """
    def __init__(self, property: str, variable: str, constant: str) -> None:
        super().__init__()
        self.property = property
        self.variable = variable
        self.constant = constant

    def __repr__(self) -> str:
        return f"<EqualTo {self.variable} {self.property} {self.constant}>"

    def to_Cypher(self) -> str:
        return f'{self.variable}.{self.property} = "{self.constant}"'

class Require(DSL):
    """
    A constraint on previous result.
    Similiar to Cypher MATCH, but more flexible
    Since Cypher MATCH requires to be used with other statement like MATCH
    But DSL Require could be used alone.

    When translation to Cypher, Require(s) will be combined into one WHERE
    And Cypher WITH statement will be used to bridge between MATCH(s) and  WHERE(s)

    Syntax:
    Require <Condition>

    Corresponding Cypher:
    WITH *
    WHERE <Condition>
    """
    def __init__(self, condition: Condition) -> None:
        super().__init__()
        self.condition = condition

    def __repr__(self) -> str:
        return f"<Require {self.condition}>"

    def to_Cypher(self, other_requires: List["Require"] = None) -> str:
        """
        Since we need to combine multiple Require to one WHERE statement
        if ```other_requires``` is not None,
        they will be translate to AND clause following this Require statement
        """
        with_str = "WITH *"
        where_str = "WHERE " + self.condition.to_Cypher()

        if other_requires:
            for require in other_requires:
                where_str += " AND " + require.condition.to_Cypher()
        
        return with_str + "\n" + where_str
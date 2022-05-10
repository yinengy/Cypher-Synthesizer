from turtle import st
from typing import List, Dict
from queue import Queue
from itertools import product, chain

from example_parser import Example
from database import CypherDatabase
import dsl

class Synthesizer:
    """
    Synthesis Cypher query from given Input/Output example
    """
    # type annotation
    example: Example
    database: CypherDatabase
    node_labels: List[str]
    node_properties: Dict[str, List[str]]
    dsl_nodes: List[dsl.Node]
    relation_labels: List[str]
    relation_properties: Dict[str, List[str]]
    dsl_relations: List[dsl.Relation]
    fixed_Return_statement: dsl.Return
    variable_to_label: Dict[str, str]
    labels_to_properties: Dict[str, List[str]]

    def __init__(self, example: Example, database: CypherDatabase) -> None:
        self.example = example
        self.database = database
        self.node_labels = []  # labels str
        self.node_properties = {}  # properties str
        self.dsl_nodes = []  # dsl object
        self.relation_labels = []
        self.relation_properties = {}
        self.dsl_relations = []
        self.fixed_Return_statement = None
        self.variable_to_label = {}
        self.labels_to_properties = {}

        self._collect_symbols()
        self._fix_Return_statement()

    def synthesize(self) -> None:
        """
        Main algorithm of the synthesizer

        1. create DSL sketch
        2. complete the sketch
        3. translate completed sketch to Cypher
        4. validate Cypher
        5. if not valid, check next sketch
        6. expand sketch
        """
        # create sketch set
        sketch = Queue()
        sketch.put([dsl.Match, dsl.Return])  # the simpliest sketch

        # pre-process target result
        # so could check if another query result match this easily
        sorted_target_result = [tuple(record.values)  for record in self.example.output]
        sorted_target_result.sort()

        for _ in range(10):  # let there be a limit on size of sketch
            # get next sketch
            sketch_to_check = sketch.get()
            
            # complete the sketch
            search_space = self._complete_sketch(sketch_to_check)

            # translate DSL to Cypher
            for dsl_program in search_space:
                cypher_statements = []
                for i, statement in enumerate(dsl_program):
                    if isinstance(statement, dsl.Require):
                        # for multiple Require statements
                        # combine them into one
                        cypher_statements.append(statement.to_Cypher(dsl_program[i+1:-1]))
                        cypher_statements.append(dsl_program[-1].to_Cypher())
                        break
                    else:
                        cypher_statements.append(statement.to_Cypher())

                query = "\n".join(cypher_statements)
                result = self.database.query(query)

                # check whether the result is valid
                if len(result) == len(self.example.output):
                    sorted_result = [tuple(record.values())  for record in result]
                    sorted_result.sort()

                    # compare two sorted tuple
                    if sorted_result == sorted_target_result:
                        return query  # found valid query
            
            # expand sketch space (program size increase by 1)
            sketch.put(sketch_to_check[:-1] + [dsl.Require, dsl.Return])  # choice 1: add a new Require
            sketch.put([dsl.Match] + sketch_to_check)  # choice 2: add a new Match

        print("reach program size limit")
        exit(1)

    def _complete_sketch(self, sketch: List[dsl.DSL.__subclasses__]) -> List[List[dsl.DSL]]:
        """
        Generate a search space with all possible assignment to the sketch
        """
        search_space_levels = []  # list of all levels of completed sketch
        possible_variables = []   # (just to speed up variable lookup) list of corresponding variables set at each level 
        for level in range(len(sketch)):  # BFS
            # each loop is a level in the tree
            # and each level contains all possible completed sketch spawned from the last level
            # example: for sketch[Match, Return]
            # level 0 is list of all possible Match statement
            # level 1 is list of all possible [Match, Return] combinations

            # create new level
            current_level = []
            current_possible_variables = []

            # get data in last level
            if level >= 1:
                last_level = search_space_levels[level - 1]
                last_possible_variables = possible_variables[level - 1]
            else:
                last_level = []
                last_possible_variables = set()

            # get the next DSL statement
            dsl_class = sketch[level]

            # complete DSL statement
            if dsl_class == dsl.Match:
                for node in self.dsl_nodes:
                    # case 1: single node
                    if not last_level:
                        current_level.append([dsl.Match(node)])
                    else:  # add new statement to every previous statements
                        current_level.extend([x + [dsl.Match(node)] for x in last_level])

                    # use set to avoid duplication
                    if not last_possible_variables:
                        current_possible_variables.append({node.variable})
                    else:
                        current_possible_variables.extend([x | {node.variable} for x in last_possible_variables])

                    # case 2: a relation with two nodes
                    for rel in self.dsl_relations:
                        for node2 in self.dsl_nodes:
                            if not last_level:
                                current_level.append([dsl.Match(node, rel, node2)])
                            else:  # add new statement to every previous statements
                                current_level.extend([x + [dsl.Match(node, rel, node2)] for x in last_level])
                            
                            if not last_possible_variables:
                                current_possible_variables.append({node.variable, rel.variable, node2.variable})
                            else:
                                current_possible_variables.extend([x | {node.variable, rel.variable, node2.variable} for x in last_possible_variables])
            elif dsl_class == dsl.Return:
                # the Return statemen is pre-processed
                # so only the variables fields are blank
                # just pick them from last level's variables list
                num_variables = len(self.fixed_Return_statement.properties)

                # Return statement will not be the first statement in the query
                # and since there exist at least a Match
                # it is gurantee that last_possible_variables and last_level is not empty
                for variable_set, previous_statements in zip(last_possible_variables, last_level):
                    # permutation with replacement of all variables
                    for variables_choice in product(variable_set, repeat=num_variables):
                        current_level.append(previous_statements + 
                            [dsl.Return(self.fixed_Return_statement.properties, variables_choice)])

                # Return statement should be the last statement
                return current_level
            elif dsl_class == dsl.Require:
                # choice 1: EqualTo
                for variable_set, previous_statements in zip(last_possible_variables, last_level):
                    for variable in variable_set:
                        label = self.variable_to_label[variable]
                        for property in self.labels_to_properties[label]:
                            for constant in self.example.constants:
                                current_level.append(previous_statements + 
                                    [dsl.Require(dsl.EqualTo(property, variable, constant))])
                                current_possible_variables.append(variable_set.copy())  # variable unchanged
            else:
                raise RuntimeError(f"Illegall DSL: {dsl_class}")

            # save current level
            search_space_levels.append(current_level)
            possible_variables.append(current_possible_variables)

    def _collect_symbols(self):
        """
        prepare node_labels, node_properties, relation_labels, relation_properties, variable_to_label
        And create corresponding DSL object.
        these will be used to complete sketch.
        """
        self.node_labels = list(self.example.nodes.keys())
        for label in self.node_labels:
            properties = self.example.nodes[label][0].properties.keys()
            self.node_properties[label] = properties
            
            # create DSL Node object, and use <node{number}> as variable
            variable = f"node{len(self.dsl_nodes)}"
            self.variable_to_label[variable] = label
            self.dsl_nodes.append(dsl.Node(label, variable))
        
        self.relation_labels = list(self.example.relations.keys())
        for label in self.relation_labels:
            properties = self.example.relations[label][0].properties.keys()
            self.relation_properties[label] = properties

            # create DSL Relation object, and use <rel{number}> as variable
            variable = f"rel{len(self.dsl_relations)}"
            self.variable_to_label[variable] = label
            self.dsl_relations.append(dsl.Relation(label, variable))

        self.labels_to_properties = self.node_properties.copy()
        self.labels_to_properties.update(self.relation_properties)

    def _fix_Return_statement(self):
        """
        Trick: the Return DSL statement is always the same across all sketchs (except variables).
        This is because part of the Return statement always match the output table.
        So we could fix it in advance to reduce search space.
        """
        properties = self.example.output[0].keys
        self.fixed_Return_statement = dsl.Return(properties, None)  # variables is left blank, will be filled later


if __name__=="__main__":
    # create database connection
    database = CypherDatabase("bolt://localhost:7687", "neo4j", "password")
    database.clear_all()

    # parse example from files
    path = "example/example2"
    example = Example(path)
    database.create_database_from_example(example)
    print(f"Synthesize on {path}\n...")

    # launch synthesizer
    synthesizer = Synthesizer(example, database)
    query = synthesizer.synthesize()
    print("Found target query:")
    print(query)
    # database.print_all()
    
    database.close()

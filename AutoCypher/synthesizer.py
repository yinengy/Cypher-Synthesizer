from example_parser import Example
from database import CypherDatabase

class Synthesizer:
    """
    Synthesis Cypher query from given Input/Output example
    """
    def __init__(self, example: Example, database: "CypherDatabase") -> None:
        self.example = example
        self.database = database

    def create_database_from_example(self) -> None:
        """
        Use input example to create a database
        """
        for nodes in self.example.nodes.values():
            for node in nodes:
                self.database.create_node(node)
        
        for relations in self.example.relations.values():
            for rel in relations:
                self.database.create_relation(rel)


if __name__=="__main__":
    # create database connection
    database = CypherDatabase("bolt://localhost:7687", "neo4j", "password")
    database.clear_all()

    # parse example from files
    example = Example("example/example1")

    # launch synthesizer
    synthesizer = Synthesizer(example, database)
    synthesizer.create_database_from_example()
    # database.print_all()
    
    database.close()

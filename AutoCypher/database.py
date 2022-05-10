from neo4j import GraphDatabase, Result
from example_parser import Example
from record import Node, Relation

class CypherDatabase:
    """
    A neo4j Cypher graph database
    """
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_all(self):
        """
        delete all nodes and relations
        """
        with self.driver.session() as session:
            session.write_transaction(self._clear_all)

    @staticmethod
    def _clear_all(tx):
        tx.run("MATCH (n)"
               "DETACH DELETE n")

    def print_all(self):
        with self.driver.session() as session:
            session.read_transaction(self._return_all_relations)
            session.read_transaction(self._return_all_nodes)

    @staticmethod
    def _return_all_relations(tx):
        relations = tx.run("MATCH ()-[r]-()"
                           "RETURN r")
        for r in relations:
            print(r)

    @staticmethod
    def _return_all_nodes(tx):
        nodes = tx.run("MATCH (n)"
                       "RETURN n")
        for n in nodes:
            print(n)

    def create_node(self, node: Node):
        """
        create node in database from Node object
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_node, node)

    @staticmethod
    def _create_node(tx, node: Node):
        tx.run(f"CREATE {node}")

    def create_relation(self, relation: Relation):
        """
        create relation in database from Relation object
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_relation, relation)

    @staticmethod
    def _create_relation(tx, relation: Relation):
        tx.run(f"MATCH {relation.src_node.str_with_variable('src')}"
               f"MATCH {relation.dst_node.str_with_variable('dst')}"
               f"CREATE (src){relation.short_repr()}(dst)")

    def create_database_from_example(self, example: Example) -> None:
        """
        Use input example to create a database
        """
        for nodes in example.nodes.values():
            for node in nodes:
                self.create_node(node)
        
        for relations in example.relations.values():
            for rel in relations:
                self.create_relation(rel)

    def query(self, query: str):
        """
        Execute a Cypher query, and return result
        Return None if query is invalid
        """
        with self.driver.session() as session:
            print("\nQuery:")
            print(query)
            result = session.read_transaction(self._query, query)

            # for record in result:
            #     print(record)
            return result
            
            
    @staticmethod
    def _query(tx, query: str):
        result = tx.run(query)
        return [record for record in result]
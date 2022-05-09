from neo4j import GraphDatabase
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

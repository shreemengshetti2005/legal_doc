from py2neo import Graph

def create_graph(uri, user, password):
    graph = Graph(uri, auth=(user, password))
    return graph

def add_clause(graph, clause, risk):
    graph.run("CREATE (c:Clause {text: $text, risk: $risk})", text=clause, risk=risk)

if __name__ == "__main__":
    g = create_graph("bolt://localhost:7687", "neo4j", "password")
    add_clause(g, "Confidentiality Clause", "Medium")

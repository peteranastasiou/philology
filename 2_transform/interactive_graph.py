
from neo4j import GraphDatabase
from neo4j import graph
import readline

# Open a connection to the graph db
URI = "neo4j://localhost"
AUTH = ("neo4j", "secretgraph")
driver = GraphDatabase.driver(URI, auth=AUTH)

driver.verify_connectivity()
driver.verify_authentication()

# Init readline so we have arrow keys in input
readline.parse_and_bind("tab: complete")
readline.set_auto_history(True)
try:
    readline.read_history_file()
except:
    pass

while True:
    s = input("> ")
    try:
        records, summary, keys = driver.execute_query(s)
        for record in records:
            print("RECORD:")
            for e in record:
                if type(e) == graph.Node:
                    print(" " + (",".join(e.labels)), e._properties)
                else:
                    print(" [:" + type(e).__qualname__ + "]", e._properties)

    except Exception as e:
        print(e)
    readline.write_history_file()

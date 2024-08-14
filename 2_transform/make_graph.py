"""
Assumes Neo4j is already running, refer script in root dir.
Reduce all words to lang:word, ignoring pos, etc for now
Pick etymologies, replacing duplicate word-relationship->word only
"""

from neo4j import GraphDatabase
from tqdm import tqdm
import json

# Open a connection to the graph db
URI = "neo4j://localhost"
AUTH = ("neo4j", "secretgraph")
driver = GraphDatabase.driver(URI, auth=AUTH)

driver.verify_connectivity()
driver.verify_authentication()

in_file = open("relationships.json")

for line in tqdm(in_file):
    # Grab json from line
    d: dict = json.loads(line)
    child = d["child_word"]
    relationship = d["relationship"]
    parent = d["parent_word"]
    source = d["source"]
    source_text = d["source_text"]
    depth = d["depth"]

    # Form query snippets
    qchild = "(c: Word {lang:$child_lang, word:$child_word})"
    qparent = "(p: Word {lang:$parent_lang, word:$parent_word})"
    qrelate = f":{relationship} "

    # Create words if they don't exist already
    driver.execute_query(
        f"MERGE {qchild}",
        child_lang=child["lang"],
        child_word=child["word"]
    )

    driver.execute_query(
        f"MERGE {qparent}",
        parent_lang=parent["lang"],
        parent_word=parent["word"]
    )

    # Create relationship if it doesn't exist already
    driver.execute_query(
        f"""MATCH {qparent}, {qchild}
        MERGE (p)-[r:PARENT_OF]->(c)
        SET r.type = $relationship,
            r.source_word = $source_word,
            r.source_lang = $source_lang,
            r.source_text = $source_text,
            r.source_depth = $source_depth""",
        child_lang=child["lang"],
        child_word=child["word"],
        parent_lang=parent["lang"],
        parent_word=parent["word"],
        source_lang=source["lang"],
        source_word=source["word"],
        source_text=source_text,
        source_depth=depth,
        relationship=relationship
    )

    exit(0)

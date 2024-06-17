"""
Extract metadata on each word in the db
include definition, year etc
"""

import json
from tqdm import tqdm
from collections import Counter

# scrape just english words
# look at languages involved in etymology
# scrape those langauges too!?
langs = ["en", "enm", "ang"]

# 1 line per json object
infile = open("snippet.json", "r")

keys = []
count = 0

for line in tqdm(infile):
    d: dict = json.loads(line)

    # Skip redirects
    if "pos" not in d:
        print(f"NO POS: {line}")
        continue
    if d["pos"] == "hard-redirect":
        # Skip it
        continue

    # Skip non-english languages
    if "lang_code" not in d:
        print("NO LANG: " + line)
        continue
    lang: str = d["lang_code"]
    if lang not in langs:
        continue

    # TODO

    count += 1

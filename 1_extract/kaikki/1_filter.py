"""
Remove entries that we probably don't want
"""

import json
from tqdm import tqdm

# 1 line per json object
in_file = open("etym0.json", "r")
out_file = open("etym1.json", "w")

count = 0
for line in tqdm(in_file):
    d: dict = json.loads(line)

    # Filter out words with spaces, probably don't want most of those
    if " " in d["word"]:
        continue

    # Filter out really long words
    if len(d["word"]) > 20:
        #print(d["word"])
        continue

    json.dump(d, out_file)
    out_file.write("\n")

    count += 1

print(f"{count} entries")  # 438,569 entries

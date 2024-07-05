"""
Remove entries that we probably don't want
"""

import json
from tqdm import tqdm

# Load top 100k words
filter_words = set()
with open("resources/wiki-100k.txt", "r") as f:
    for line in f:
        word: str = line.strip()
        if len(word) > 0 and word[0] != '#':
            filter_words.add(word)

# 1 line per json object
in_file = open("etym0.json", "r")
out_file = open("etym1.json", "w")

count = 0
for line in tqdm(in_file):
    d: dict = json.loads(line)

    word: str = d["word"]

    # Filter out words with spaces, probably don't want most of those
    if " " in word:
        continue

    # Skip all single letters of the alphabet that aren't really words
    if len(word) == 1 and word.lower() not in ["a", "i"]:
        continue

    # Filter out really long words
    if len(word) > 20:
        #print(d["word"])
        continue

    if word not in filter_words:
        continue

    json.dump(d, out_file)
    out_file.write("\n")

    count += 1

print(f"{count} entries")  # 438,569 entries

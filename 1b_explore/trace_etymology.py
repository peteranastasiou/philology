"""
Transform from each entry having a complete etymology,
to each one having a list of direct parents (derived-from)
"""

# Initial questions:
# do we have many duplicates of "lang:word"?
#   yes, some with different pos
# do we have many duplicates of "lang:word:pos"?
#   yes, different meanings for same pos
#
# keep it simple and combine (lang:word)
#  by having lists for pos, glosses, derived-from

import json
from tqdm import tqdm

# obj = {
#     "word": d["word"],
#     "pos": d["pos"],
#     "lang": d["lang"],
#     "lang_code": d["lang_code"],
#     "etymology_text": d["etymology_text"],
#     "etymology_templates": d["etymology_templates"],   # Can use name: der/ name: root to determine etymology!
#     "glosses": defns
# }

# 1 line per json object
in_file = open("snippet.json", "r")
out_file = open("etym2.json", "w")

# dictionary of "lang:word" -> {derived_from: [], glosses: [], pos: [], ...}
word_dict = {}

def get_entry(lang_code, word):
    word_id = f"{lang_code}:{word}"
    if word_id in word_dict:
        return word_dict[word_id]
    else:
        d = {}
        word_dict[word_id] = d
        return d

def add_unique(array: list, data):
    if data not in array:
        array.append(data)

def parse_etymology(text, templates):
    pass

count = 0
for line in tqdm(in_file):
    d: dict = json.loads(line)

    entry = get_entry(d["lang_code"], d["word"])
    # add_unique(entry["glosses"], d["glosses"]) # TODO flatten glosses

    print(d["etymology_text"])

    # json.dump(d, out_file)
    # out_file.write("\n")

    count += 1

print(f"{count} entries")  # 438,569 entries

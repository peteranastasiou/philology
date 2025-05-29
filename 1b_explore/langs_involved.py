import json
from tqdm import tqdm
from collections import Counter

# 1 line per json object
in_file = open("etym1.json", "r")  # etym1
out_file = open("parent_langs.tsv", "w")

langs = {}

# Short hand to get a template arg (if it exists)
def targ(t, key):
    if key not in t["args"]:
        return None
    return t["args"][key]

for line in tqdm(in_file):
    d: dict = json.loads(line)

    tmpl = d["etymology_templates"]
    has_pie_root = False
    for t in tmpl:
        if t["name"] in ["der", "inh", "root", "bor"]:
            lang = targ(t, "2")
            if lang in ["EL."]:
                print(json.dumps(d, indent=2))


print(langs)
import json
from tqdm import tqdm
from collections import Counter

# 1 line per json object
in_file = open("etym1.json", "r")  # etym1
out_file = open("parent_langs.tsv", "w")

# Only list languages from etymologies which aren't traced back to PIE
# This indicates we should
only_langs_from_possibly_incomplete_etym = True

lang = []

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
            if targ(t, "2") == "ine-pro":
                has_pie_root = True
    if not only_langs_from_possibly_incomplete_etym or not has_pie_root:
        for t in tmpl:
            if t["name"] in ["der", "inh", "root", "bor"]:
                lang.append(targ(t, "2"))

# pprint(others)

print("-------")
c = dict(Counter(lang))
lang_occurance = sorted(
    [(k, c[k]) for k in c],
    key=lambda x: x[1],
    reverse=True
)
for l in lang_occurance:
    print(f"{l[0]}\t{l[1]}")
    out_file.write(f"{l[0]}\t{l[1]}\n")

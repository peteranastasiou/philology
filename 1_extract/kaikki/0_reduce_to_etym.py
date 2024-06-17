import json
from tqdm import tqdm
from collections import Counter

# scrape just english words
# look at languages involved in etymology
# scrape those langauges too!?
langs = ["en", "enm", "ang"]

# 1 line per json object
in_file = open("resources/raw-wiktextract-data.json", "r")

out_file = open("etym0.json", "w")
fail_out_file = open("resources/etym0.failed.json", "w")

keys = []
count = 0

# Takes about 6 mins on my machine
for line in tqdm(in_file):
    d: dict = json.loads(line)

    # Skip redirects
    if "pos" not in d:
        print(f"NO POS: {line}")
        continue
    if d["pos"] == "hard-redirect":
        # Skip it
        continue

    # Skip non-english languages
    if "lang_code" not in d or "lang" not in d:
        print("NO LANG: " + line)
        continue
    lang: str = d["lang_code"]
    if lang not in langs:
        continue

    if "etymology_text" not in d:
        # No etymology
        continue

    # Investigate cases without etymology_templates
    if "etymology_templates" not in d:
        # has an etymology we can't parse easily:
        fail_out_file.write(line)
        continue

    # Collect glosses (definitions)
    defns = []
    if "senses" in d:
        for s in d["senses"]:
            if "glosses" in s:
                defns.append(s["glosses"])

    obj = {
        "word": d["word"],
        "pos": d["pos"],
        "lang": d["lang"],
        "lang_code": d["lang_code"],
        "etymology_text": d["etymology_text"],
        "etymology_templates": d["etymology_templates"],   # Can use name: der/ name: root to determine etymology!
        "glosses": defns
    }
    json.dump(obj, out_file)
    out_file.write("\n")

    count += 1

print(f"{count} entries")  # 453,848 entries
print(Counter(keys))

"""
Deduce structure and meaning of undocumented etymology templates
"""

"""
etymology_template deduced structure and meaning:
Asterisk indicates more investigation required

name:
    der=derived, parent word
        args:
            1: lang code of current
            2: lang code of parent
            3: parent word (or "-" ???)
            4: "", optional
            5: description, optional

    inh=inherited? in sequence of derivations, in line with der
        args:
            1: lang code of current
            2: lang code of parent
            3: parent word
            id: ? e.g. "adjectival", ...

*   inh+=? seems to repeat an above inh? can be ignored?

*   root=ultimate root. does it skip step? - need to check
        args: same as for der

*   bor=borrowed? not in line with der/inh (refer eng:troll)!
        args:
            1: lang code of current
            2: lang code of parent
            3: parent word
            tr: ?, optional
            lit: translation?, optional

    suf=suffix? parallel to above derivation, shows combination of part1+part2 => word
        args:
            1: lang code of current
            2: part1
            3: part2
            id2: ? e.g. "adjectival", ...

    cog: cognate
        can be skipped as cognates will emerge from the tree display

*    af? seems to show an equivalent word
*   affix
*   blend
*   clipping
*   compound
*   lbor
*   m+
*   prefix

    nb...: other forms not shown in etymology text - ignore.
    glossary: does not seem to be a meaningful extraction
    etymid: does not seem to have a consistent or meaningful template
    sup: not meaningful?
    doublet: what is a doublet?
    senseno: what is a senseno?

"""

import json
# from tqdm import tqdm

# Filter on etymologies which have this template name:
filter_name = "root"

# Don't print these templates
ignore_templates = ["nb...", "glossary", "cog", "etymid"]
#keep_templates = ["der", "inh", "bor", "suf", "doublet"]

def pprint(o):
    print(json.dumps(o, indent=2))

# 1 line per json object
in_file = open("snippet.json", "r")  # etym1
out_file = open("roots.json", "w")

roots = set()
relations = set()

count = 0
for line in in_file:
    d: dict = json.loads(line)

    tmpl = d["etymology_templates"]
    # print(tmpl)

    template_names = [t["name"] for t in tmpl]
    for name in template_names:
        relations.add(name)

    # Only print out etymologies incl template_name we are interested in
    if filter_name in template_names:

        print("\n\n" + d["lang"] + ":" + d["word"])
        print(d["etymology_text"])
        print(d)
        for t in tmpl:
            if t["name"] not in ignore_templates:
                pprint(t)

# pprint(others)

print("-------")
print(sorted(relations))
print(f"{count} entries")  # 438,569 entries

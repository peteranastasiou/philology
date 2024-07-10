
import json
from tqdm import tqdm

# maps of template name -> rename
parent_templates = {
    "derived": "derived",
    "der": "derived",
    "borrowed": "borrowed",
    "bor": "borrowed",
    "learned borrowing": "borrowed",
    "lbor": "borrowed",
    "orthographic borrowing": "borrowed",
    "obor": "borrowed",
    "inherited": "inherited",
    "inh": "inherited",
}

combination_templates = {
    "affix": "affix",
    "af": "affix",
    "compound": "compound",
    "com": "compound",
    "confix": "confix",
    "con": "confix",
    "prefix": "prefix",
    "pre": "prefix",
    "suffix": "suffix",
    "suf": "suffix",
    "blend": "blend",
}

ignored_templates = [
    "cog",
    "ncog",
    "smallcaps",
    "doublet",
]

prop_names = [
    "pos", # part of speech e.g. noun
    "id", # ??? needs investigation
    "t", # translation
    "lit", # literal translation
    "tr", # transliteration
]

def pprint(o):
    print(json.dumps(o, indent=2))

# Short hand to get a template arg (if it exists)
def arg(t, key):
    if key not in t["args"]:
        return None
    return t["args"][key]

def arg_as_prop(o, t, key, prop_key=None):
    a = arg(t, key)
    if a:
        o[prop_key or key] = a

def parse_parent(t):
    # arguments: 1=curr-lang 2=parent-lang 3=parent-word
    # optional args: pos, id
    relationship = parent_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page
    parent_lang = arg(t, "2")
    parent_word = arg(t, "3")

    if not parent_word or parent_word == "-":
        # Skip it, no word given
        return

    # Properties
    props = {}
    for p in prop_names:
        arg_as_prop(props, t, p)

    print(f"parent: {lang} <-[{relationship}]- {parent_lang}:{parent_word} {props}")
    #pprint(t)

def parse_combination(t):
    # format: 1=curr-lang 2=parent-word 3=parent-word [n=....]
    # optional params: posX, idX where X is 1,2,...n corresponding to parent word
    # where parent word MAY have lang-code: prefix (only confirmed for affix in the doc)
    # Note: watch out for automatic addition of hyphen to parts
    relationship = combination_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page
    words = []
    pprint(t)
    words.append({"word": arg(t, "2")})
    words.append({"word": arg(t, "3")})
    # iterate through all contributing words
    for i in range(4, 10):
        w = arg(t, f"{i}")
        if not w:
            break
        words.append({"word": w})

    for i, w in enumerate(words):
        for p in prop_names:
            # Lookup props by index e.g. pos1 for word one
            arg_as_prop(w, t, f"{p}{i+1}", p)
    print(f"combination: {lang} <-[{relationship}]-")
    for w in words:
        print(f" - {w}")


def parse(word_id, t):
    name = t["name"]
    if name in parent_templates:
        parse_parent(t)
    elif name in combination_templates:
        parse_combination(t)
    elif name in ignored_templates:
        pass
    else:
        print(f"unused template: {name}")


# 1 line per json object
in_file = open("snippet.json", "r")
out_file = open("roots.json", "w")

for line in in_file:
    d: dict = json.loads(line)
    lang = d["lang_code"]
    word = d["word"]
    pos = d["pos"]
    word_id = f"{lang}:{word}:{pos}"
    templates = d["etymology_templates"]

    print("__________")
    print(word_id)
    print('"'+d["etymology_text"]+'"')
    for t in templates:
        parse(word_id, t)

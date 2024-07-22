
import json
from tqdm import tqdm
import re

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

known_langs = set()
f = open("langcodes.tsv")
for i, line in enumerate(f):
    if i != 0:
        parts = line.split('\t')
        known_langs.add(parts[0])
unknown_langs = set()

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

def parse_word(t, key):
    """
        Outputs word, props
        Note: raw is of the form: [lang:]word[#disambiguator][<attr:value>]*[<tag>value</tag>]*
    """
    raw: str = arg(t, key)
    if not raw: return None, None

    # Separate prefix from tags
    word = raw
    tags = ""
    i = raw.find("<")
    if i >= 0:
        word = raw[:i]
        tags = raw[i:]

    if not word:
        print(f"Failed to parse word: {raw.encode('utf-8')}")
        return None, None

    props = {}

    # Strip off lang code if present
    i = word.find(":")
    if i > 0:
        lang = word[:i]
        word = word[i+1:]
        props['lang'] = lang

    # Strip off disambiguator hash if present - is this a page section reference?
    i = word.find("#")
    if i > 0:
        disambiguator = word[i+1:]
        word = word[:i]
        props['disambiguator'] = disambiguator

    if tags:
        if "</" in tags:
            print("Open/close tags are not supported:")
            print("  ", word, tags)
        else:
            # print(raw.encode("utf-8"))
            for tag in re.findall("<[^>]*>", tags):
                contents = tag[1:-1]  # strip off start and end tag
                parts = contents.split(":")
                if len(parts) != 2:
                    print("Invalid tag: ", tag)
                    continue
                props[parts[0]] = parts[1]

    return word, props


def parse_parent(word_id, t):
    # arguments: 1=curr-lang 2=parent-lang 3=parent-word
    # optional args: pos, id
    relationship = parent_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page
    parent_lang = arg(t, "2")
    parent_word, props = parse_word(t, "3")

    if not parent_word or parent_word == "-":
        # Skip it, no word given
        return

    if parent_lang not in known_langs:
        print("UNKNOWN LANG:" + parent_lang + " for "+word_id)
        # pprint(t)
        unknown_langs.add(parent_lang)
        return

    # Pull additional properties
    for p in prop_names:
        arg_as_prop(props, t, p)

    print(f"parent-type: {word_id} {lang} <-[{relationship}]- {parent_lang}:{parent_word} {props}")
    #pprint(t)

def parse_combination(word_id, t):
    # format: 1=curr-lang 2=parent-word 3=parent-word [n=....]
    # optional params: posX, idX where X is 1,2,...n corresponding to parent word
    # where parent word MAY have lang-code: prefix (only confirmed for affix in the doc)
    # Note: watch out for automatic addition of hyphen to parts
    relationship = combination_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page
    words = []
    # pprint(t)
    words.append({"word": arg(t, "2")})
    words.append({"word": arg(t, "3")})

    # word1, attr1 = parse_word(t, "2")
    # word2, attr2 = parse_word(t, "3")

    # iterate through all contributing words
    for i in range(4, 10):
        w = arg(t, f"{i}")
        if not w:
            break
        words.append({"word": w})

    for i, w in enumerate(words):
        word = w['word']

        for p in prop_names:
            # Lookup props by index e.g. pos1 for word one
            arg_as_prop(w, t, f"{p}{i+1}", p)
    # print(f"combination: {lang} <-[{relationship}]-")
    # for w in words:
    #     print(f" - {w}")


def parse(word_id, t):
    name = t["name"]
    if name in parent_templates:
        parse_parent(word_id, t)
    elif name in combination_templates:
        parse_combination(word_id, t)
    elif name in ignored_templates:
        pass
    else:
        pass
        # print(f"unused template: {name}")


# 1 line per json object
in_file = open("etym1.json", "r")
out_file = open("roots.json", "w")

for line in in_file:
    d: dict = json.loads(line)
    lang = d["lang_code"]
    word = d["word"]
    pos = d["pos"]
    word_id = f"{lang}:{word}:{pos}"
    templates = d["etymology_templates"]

    # print("__________")
    # print(word_id)
    # print('"'+d["etymology_text"]+'"')
    for t in templates:
        parse(word_id, t)

print("Unknown langs: "+str(unknown_langs))


import json
from tqdm import tqdm
import re

VERBOSE = False

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

# Note: templates get confusing e.g. suffix template can contain all elements of a word
# Thus, just call everything an affix
combination_templates = {
    "affix": "affix",
    "af": "affix",
    "confix": "affix",
    "con": "affix",
    "prefix": "affix",
    "pre": "affix",
    "suffix": "affix",
    "suf": "affix",
    "compound": "compound",
    "com": "compound",
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

# 1 line per json object
in_file = open("etym1.json", "r")
out_file = open("relationships.json", "w")

def pprint(o):
    print(json.dumps(o, indent=2))

context = ""

if VERBOSE:
    vprint = print
else:
    def vprint(*args, **kwargs):
        pass

def format_word_id(word):
    s = f"{word['word']}:{word['lang']}"
    if "pos" in word:
        return f"{s}#{word['pos']}"
    return s

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
        Multiple aliases may be listed separated by ", "
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

    if ", " in word:
        aliases = word.split(", ")
        word = aliases[0]
        props["aliases"] = aliases[1:]

    return word, props

def parse_word_as_dict(t, arg):
    w, p = parse_word(t, arg)
    if not w:
        return None
    p["word"] = w
    return p

def parse_parent(child_word: dict, t: dict) -> dict:
    # arguments: 1=curr-lang 2=parent-lang 3=parent-word
    # optional args: pos, id
    relationship = parent_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page
    parent_lang = arg(t, "2")
    parent_word = parse_word_as_dict(t, "3")

    if not parent_word or parent_word['word'] == "-":
        # Skip it, no word given
        return None

    if parent_lang not in known_langs:
        print("UNKNOWN LANG:" + parent_lang + " for " + str(child_word))
        # pprint(t)
        unknown_langs.add(parent_lang)
        return None

    parent_word["lang"] = parent_lang

    # Pull additional properties
    for p in prop_names:
        arg_as_prop(parent_word, t, p)

    vprint(f"{format_word_id(child_word):30s} <--{relationship:10s} {format_word_id(parent_word)}")

    # Write out to file
    out_obj = {
        "child_word": child_word,
        "relationship": relationship,
        "parent_word": parent_word
    }
    out_str = json.dumps(out_obj)
    out_file.write(out_str+"\n")

    return parent_word

def parse_combination(child_word: dict, t: dict) -> dict:
    # format: 1=curr-lang 2=parent-word 3=parent-word [n=....]
    # optional params: posX, idX where X is 1,2,...n corresponding to parent word
    # where parent word MAY have lang-code: prefix (only confirmed for affix in the doc)
    # Note: watch out for automatic addition of hyphen to parts
    relationship = combination_templates[t["name"]]
    lang = arg(t, "1")  # Mostly useless, just indicates language of page

    # There are at least 2 words (args "2" & "3")
    word1 = parse_word_as_dict(t, "2")
    word2 = parse_word_as_dict(t, "3")

    if not word1 and not word2:
        print("Cannot parse combination: " + json.dumps(t))
        return None

    words = []
    if word1: words.append(word1)
    if word2: words.append(word2)

    # iterate through all remaining words (args "4", ...)
    for i in range(4, 10):
        w = parse_word_as_dict(t, f"{i}")
        if not w:
            break
        words.append(w)

    for i, w in enumerate(words):
        for p in prop_names:
            # Lookup props by index e.g. pos1 for word one
            arg_as_prop(w, t, f"{p}{i+1}", p)

    # If the word has no language tag, we must assume it is the same as child
    for w in words:
        if "lang" not in w:
            w["lang"] = child_word["lang"]

    vprint(f"{format_word_id(child_word):30s} <--{relationship:10s}",
          " + ".join([format_word_id(w) for w in words]))

    for w in words:
        # Write out to file
        out_obj = {
            "child_word": child_word,
            "relationship": relationship,
            "parent_word": w
        }
        out_str = json.dumps(out_obj)
        out_file.write(out_str+"\n")

    return None # No future parents expected, as past diverges

def parse(word: dict, t):
    name = t["name"]
    if name in parent_templates:
        return parse_parent(word, t)
    elif name in combination_templates:
        return parse_combination(word, t)
    elif name in ignored_templates:
        return None
    else:
        vprint(f"Unused template: {name}")
        return None


for line in tqdm(in_file):
    d: dict = json.loads(line)

    # Form the first word (the page's word)
    lang = d["lang_code"]
    word = d["word"]
    pos = d["pos"]
    child_word = {"word": word, "lang": lang, "pos": pos}

    vprint("__________")
    vprint(word)
    vprint('"'+d["etymology_text"]+'"')
    context = word + '\n' + d['etymology_text'] + "\n" + json.dumps(d["etymology_templates"], indent=2)

    # Walk history, assuming each derived word is a parent of the previous
    curr_word = child_word
    for t in d["etymology_templates"]:
        parent_word = parse(curr_word, t)
        if parent_word is None:
            # Skip this relationship
            # TODO decide when to reset to child word!
            pass
        else:
            curr_word = parent_word

print("Unknown langs: "+str(unknown_langs))

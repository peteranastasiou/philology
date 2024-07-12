# out file
fo = open("langcodes.tsv", "w")

# semicolon separated file from https://en.wiktionary.org/wiki/Wiktionary:List_of_languages,_csv_format
f = open("langs.ssv")
for line in f:
    parts = line.split(";")
    fo.write(f"{parts[1]}\t{parts[2]}\n")

f = open("langs_etym.ssv")
for line in f:
    parts = line.split(";")
    fo.write(f"{parts[1]}\t{parts[2]}\n")

# Additional langs which aren't in the above for some reason,
# deduced from etymology template expansions
fo.write(
"""ML.	Medieval Latin
prv	Provençal
EL.	Ecclesiastical Latin
LL.	Late Latin
RL.	Renaissance Latin
VL.	Vulgar Latin
CL.	Classical Latin
NL.	New Latin
roa	Romance
cel-bry	Brythonic
ira-old	Old Iranian
gem	Germanic
gmq	North Germanic""")
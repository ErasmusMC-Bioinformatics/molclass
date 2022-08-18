import re

TRANSCRIPT_RE = "(?P<transcript>NM_?[0-9]+)"

"""
http://www.hgvs.org/mutnomen/examplesDNA.html
c.-12G>A
c.1A>C
c.23G>C
c.88+2T>G
c.89-1G>T
c.123+89C>T
c.329G>C
c.*70T>A
c.*293C>A

c.13del
c.13delG
c.4del
c.4delG
c.301-3del
c.301-3delT
c.-11_-4del
c.92_94del
c.92_94delGAC
c.*8_*21del
c.120_123+48del
c.124-12_129del
c.7_8del
c.7_8delTG
c.123del
c.123delA
c.13-?_300+?del

c.(?_-30)_(*220_?)del
c.13-23_301-143del

c.13dup
c.13dupG
c.92_94dup
c.92_94dupGAC
c.120_123+48dup
c.7_8dup
c.7_8dupTG

c.51_52insT
c.51_52insGAGA

c.123+54_123+55insAB012345.1

c.*70_71[6]
c.*70CA[6]
c.*70_71[8]
c.*70CA[8]
c.*70_71[6];[11]
c.*70CA[6];[11]

c.77_80inv
c.77_80invCTGA
c.1670_1673inv

c.1023_1024delinsAT
c.1670_1673delinsTTCC

"""
C_DOT_RE_LIST = [re.compile(regex, re.IGNORECASE) for regex in [
    # all?
    "(?P<cdot>c[.](?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)(?P<cdot_ref>[actg]+)?(?P<cdot_type>dup|delins|del|ins|>|&gt;|inv)(?P<cdot_alt>[actg]+)?)",
    # sub
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_][0-9]+)?)(?P<cdot_ref>[acgt]+)([>]|&gt;)(?P<cdot_alt>[actg]+)",
    # del
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)del(?P<cdot_ref>[actg]+)?",
    # dup
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)dup(?P<cdot_ref>[actg]+)?",
    # ins
    # "",
    # repeat
    "(?P<cdot>c[.](?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_][0-9]+)?)(?P<cdot_ref>[actg]+)?\[(?P<cdot_repeats>[0-9]+)\](;\[(?P<cdot_repeats2>[0-9]+)\])?)"
]]

# https://www.hgmd.cf.ac.uk/docs/cd_amino.html
# https://regex101.com/r/rMLj6y/1
"""
p.Trp24Cys
p.(Trp24Cys)
p.Trp24Ter
p.Trp24*
p.Cys188=
p.Met1?
p.Gln2366Lys
p.Trp26Cys
p.Trp26Ter
p.Trp26*

p.Trp26_Leu833del
p.Leu2_Met124del
p.Met1_Leu2insArgSerThrVal
p.Met1ext-5
p.(Gly56Ala^Ser^Cys)
p.Trp24_Val25delinsCysArg

p.?
p.0
p.0?
"""
P_DOT_RE_LIST = [re.compile(regex, re.IGNORECASE) for regex in [
    # missense, nonsense and silent 
    "(?P<pdot>p[.](?P<pdot_from>[a-z*]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[a-z*=?]+))",
    # predicted missense, nonsense and silent
    "(?P<pdot>p[.]\((?P<pdot_from>[a-z*]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[a-z*=?]+)\))",
    # del
    "(?P<pdot>p[.](?P<pdot_from>(?P<pdot_del_from>[a-z*]+)(?P<pdot_del_from_pos>[0-9]+)_(?P<pdot_del_to>[a-z]+)(?P<pdot_del_to_pos>[0-9]+))del)",
    # dup
    "(?P<pdot>p[.](?P<pdot_from>(?P<pdot_dup_from>[a-z*]+)(?P<pdot_dup_from_pos>[0-9]+)_(?P<pdot_dup_to>[a-z]+)(?P<pdot_dup_to_pos>[0-9]+))dup)",
    # ins
    "(?P<pdot>p[.](?P<pdot_from>(?P<pdot_del_from>[a-z*]+)(?P<pdot_del_from_pos>[0-9]+)_(?P<pdot_del_to>[a-z]+)(?P<pdot_del_to_pos>[0-9]+))ins(?P<pdot_to>[^\d\s^)_]+))",
    # delins
    "(?P<pdot>p[.](?P<pdot_from>(?P<pdot_del_from>[a-z*]+)(?P<pdot_del_from_pos>[0-9]+)_(?P<pdot_del_to>[a-z]+)(?P<pdot_del_to_pos>[0-9]+))delins(?P<pdot_to>[^\d\s^)_]+))",
    # no protein produced, unkown effect and splicing
    "p\.(0|0\?|\?|\(=\)|=)",

]]

TRANSCRIPT_STR = "(?P<transcript>NM_?[0-9]+([.][0-9]+)?)"
TRANSCRIPT_RE = re.compile(TRANSCRIPT_STR, re.IGNORECASE)

# gene regex for gene:cdot search
GENE_CDOT_STR = "\s*(?P<gene>[^:]+)"

CHR_POS_END_REF_ALT_STR = "(?P<chr>(chr)?[0-9]+)[\s:_-]+(?P<pos>[0-9]+)[\s:_-]+(?P<end>[0-9]+)?(?P<ref>[actg]+)[\s:_-]+(?P<alt>[actg]+)"
CHR_POS_END_REF_ALT_RE = re.compile(CHR_POS_END_REF_ALT_STR, re.IGNORECASE)

RS_RE = re.compile("(?P<rs>rs[0-9]+)", re.IGNORECASE)

def parse_rs(search) -> dict:
    result = {}
    if m := RS_RE.search(search):
        result.update(m.groupdict())
    return result

def parse_transcript(search) -> dict:
    result = {}
    if m := TRANSCRIPT_RE.search(search):
        result.update(m.groupdict())
    return result

def parse_cdot(search) -> dict:
    result = {}
    for regex in C_DOT_RE_LIST:
        if m := regex.search(search):
            result.update(m.groupdict())
    return result

def parse_gene_cdot(search) -> dict:
    result = {}
    for regex in C_DOT_RE_LIST:
        cdot = regex.pattern
        pattern = f"{GENE_CDOT_STR}:{cdot}"
        
        if m := re.search(pattern, search, re.IGNORECASE):
            m = m.groupdict()
            m["gene_cdot"] = m["cdot"]
            del m["cdot"]
            result.update(m)
    return result

def parse_pdot(search) -> dict:
    result = {}
    for regex in P_DOT_RE_LIST:
        if m := regex.search(search):
            result.update(m.groupdict())
    return result

def parse_pos(search):
    result = {}
    if m := CHR_POS_END_REF_ALT_RE.search(search):
        result.update(m.groupdict())
    return result

def parse_search(search) -> dict:
    result = parse_rs(search)

    transcript = parse_transcript(search)
    if transcript:
        result.update(transcript)
        result.update(parse_cdot(search))
        
    else:  # gene:cdot check
        result.update(parse_gene_cdot(search))  

    if "cdot" in result or "gene_cdot" in result:
        result["ref"] = result["cdot_ref"]
        result["alt"] = result["cdot_alt"]

    result.update(parse_pdot(search))

    result.update(parse_pos(search))

    return result
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
"""
C_DOT_RE_LIST = [re.compile(regex, re.IGNORECASE) for regex in [
    # all?
    "(?P<cdot>c[.](?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)(?P<cdot_ref>[actg]+)?(?P<cdot_type>dup|del|ins|>|&gt;|inv)(?P<cdot_alt>[actg]+)?)",
    # sub
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_][0-9]+)?)(?P<cdot_ref>[acgt]+)([>]|&gt;)(?P<cdot_alt>[actg]+)",
    # del
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)del(?P<cdot_ref>[actg]+)?",
    # dup
    # "(?P<cdot>c[.])(?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_*]+[0-9?]+)?(?P<cdot_pos3>[-+_*]+[0-9]+)?(?P<cdot_pos4>[-+_*]+[0-9?]+)?)dup(?P<cdot_ref>[actg]+)?",
    # ins
    # "",
    # repeat
    "(?P<cdot>c[.](?P<cdot_pos>[-*]?[0-9]+(?P<cdot_pos2>[-+_][0-9]+)?)(?P<cdot_ref>[actg]+)?[[](?P<cdot_repeats>[0-9]+)[]](;[[](?P<cdot_repeats2>[0-9]+)[]])?)"
]]
# https://regex101.com/r/Hxag8o/1
C_DOT_STR = "(?P<cdot>c[.](?P<cdot_pos>[0-9*]+([_+-][0-9]+(-[0-9]+)?)?)(?P<cdot_from>[actg]+)?(?P<type>&gt;|[>]|del|ins)(?P<cdot_to>[actg]+))"
C_DOT_RE = re.compile(C_DOT_STR, re.IGNORECASE)

# https://regex101.com/r/Hxag8o/1
P_DOT_STR = "(?P<pdot>\s*[(]p[.](?P<pdot_from>[^0-9]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[^\s\n]+))"
P_DOT_RE = re.compile(P_DOT_STR, re.IGNORECASE)

TRANSCRIPT_STR = "(?P<transcript>NM_?[0-9]+([.][0-9]+)?)"
TRANSCRIPT_RE = re.compile(TRANSCRIPT_STR, re.IGNORECASE)

CHR_POS_END_REF_ALT_STR = "(?P<chr>(chr)?[0-9])+\s+(?P<pos>[0-9]+)\s+(?P<end>[0-9]+)?(?P<ref>[actg])\s+(?P<alt>[actg])"
CHR_POS_END_REF_ALT_RE = re.compile(CHR_POS_END_REF_ALT_STR, re.IGNORECASE)

RS_RE = re.compile("(?P<rs>rs[0-9]+)", re.IGNORECASE)


def parse_search(search) -> dict:
    result = {}
    if m := RS_RE.search(search):
        result.update(m.groupdict())

    if m := TRANSCRIPT_RE.search(search):
        result.update(m.groupdict())

    for regex in C_DOT_RE_LIST:
        if m := regex.search(search):
            result.update(m.groupdict())

    if m := CHR_POS_END_REF_ALT_RE.search(search):
        result.update(m.groupdict())
    
    return result
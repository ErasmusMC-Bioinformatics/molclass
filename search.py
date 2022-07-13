import re

TRANSCRIPT_RE = "(?P<transcript>NM_?[0-9]+)"

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

    if m := C_DOT_RE.search(search):
        result.update(m.groupdict())

    if m := CHR_POS_END_REF_ALT_RE.search(search):
        result.update(m.groupdict())
    
    return result
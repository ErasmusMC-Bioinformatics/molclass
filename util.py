import os
import sys
# https://molbiol-tools.ca/Amino_acid_abbreviations.htm
protein_conversion = {
    "Ala": 	"A",
    "Arg": 	"R",
    "Asn": 	"N",
    "Asp": 	"D",
    "Asx": 	"B",
    "Cys": 	"C",
    "Glu": 	"E",
    "Gln": 	"Q",
    "Glx": 	"Z",
    "Gly": 	"G",
    "His": 	"H",
    "Ile": 	"I",
    "Leu": 	"L",
    "Lys": 	"K",
    "Met": 	"M",
    "Phe": 	"F",
    "Pro": 	"P",
    "Ser": 	"S",
    "Thr": 	"T",
    "Trp": 	"W",
    "Tyr": 	"Y",
    "Val": 	"V",
    "Ter":  "*",
}

def get_pdot_abbreviation(pdot: str):
    for full, abbr in protein_conversion.items():
        pdot = pdot.replace(full, abbr)
    return pdot

rev_compl_dic = {
    "c": "g",
    "C": "G",
    "g": "c",
    "G": "C",
    "t": "a",
    "T": "A",
    "A": "T",
    "a": "t",
}

def reverse_complement(input: str):
    return "".join([rev_compl_dic[c] for c in input])

def relative_path(path: str) -> str:
    """
    Paths are different from within a PyInstaller package, this function figures that out
    https://pyinstaller.org/en/stable/runtime-information.html#run-time-information
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    else:
        return os.path.join(".", path)
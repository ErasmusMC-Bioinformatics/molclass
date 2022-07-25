
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
}

def get_pdot_abbreviation(pdot: str):
    for full, abbr in protein_conversion.items():
        pdot = pdot.replace(full, abbr)
    return pdot
from templates import templates

# generate this by saving the gene grid page:
# https://ckb.jax.org/gene/grid
# and running parse_gene_html below on it
gene_dict = {"ABL1": 25, "ALK": 238, "APC": 324, "ARID1A": 8289, "ATM": 472, "ATR": 545, "ATRX": 546, "BARD1": 580, "BRAF": 673, "BRIP1": 83990, "CBL": 867, "CDK12": 51755, "CDKN2A": 1029, "CHEK1": 1111, "CHEK2": 11200, "CSF3R": 1441, "CTNNB1": 1499, "DNMT3A": 1788, "EML4": 27436, "FANCA": 2175, "FANCL": 55120, "FBXW7": 55294, "FGFR1": 2260, "FGFR2": 2263, "FGFR3": 2261, "FLT3": 2322, "HRAS": 3265, "IDH1": 3417, "IDH2": 3418, "JAK2": 3717, "JAK3": 3718, "KIT": 3815, "KMT2A": 4297, "MAP2K1": 5604, "MLH1": 4292, "MSH6": 2956, "NRAS": 4893, "PALB2": 79728, "PIK3CA": 5290, "PTEN": 5728, "RAD51B": 5890, "RAD51C": 5889, "RAD51D": 5892, "RAD54L": 8438, "RB1": 5925, "RET": 5979, "ROS1": 6098, "TET2": 54790, "TP53": 7157, "VHL": 7428, "A1CF": 29974, "ABCA10": 10349, "ABCB1": 5243, "ABCC1": 4363, "ABCC10": 89845, "ABCC4": 10257, "ABCG2": 9429, "ABL2": 27, "ABR": 29, "ABRAXAS1": 84142, "ACBD5": 91452, "ACLY": 47, "ACOX1": 51, "ACP3": 55, "ACSL6": 23305, "ACTA2": 59, "ACTB": 60, "ACTC1": 70, "ACTG2": 72, "ACTL6A": 86, "ACVR1": 90, "ACVR1B": 91, "ACVRL1": 94, "ADAM17": 6868, "ADAM18": 8749, "ADAM9": 8754, "ADAR": 103, "ADARB1": 104, "ADGRA2": 25960, "ADORA2A": 135, "AEBP2": 121536, "AFAP1": 60312, "AFAP1L2": 84632, "AFDN": 4301, "AFF1": 4299, "AFF2": 2334, "AFF3": 3899, "AFF4": 27125, "AFP": 174, "AGAP1": 116987, "AGAP3": 116988, "AGBL4": 84871, "AGGF1": 55109, "AGK": 55750, "AGO1": 26523, "AGO2": 27161, "AGO3": 192669, "AGO4": 192670, "AGTRAP": 57085, "AHCYL1": 10768, "AHCYL2": 23382, "AICDA": 57379, "AIM2": 9447, "AKAP13": 11214, "AKAP4": 8852, "AKAP9": 10142, "AKR1C3": 8644, "AKT1": 207, "AKT2": 208, "AKT3": 10000, "ALCAM": 214, "ALOX12B": 242, "ALPK1": 80216, "AMER1": 139285, "AMPD2": 271, "ANGPT1": 284, "ANGPT2": 285, "ANGPTL4": 51129, "ANK3": 288, "ANKRD1": 27063, "ANKRD11": 29123, "ANKRD26": 22852, "ANXA1": 301, "ANXA5": 308, "AP1M1": 8907, "APLNR": 187, "APOBEC1": 339, "APOBEC2": 10930, "APOBEC3A": 200315, "APOBEC3C": 27350, "APOBEC3D": 140564, "APOBEC3F": 200316, "APOBEC3G": 60489, "APOBEC4": 403314, "APP": 351, "AQP1": 358, "AR": 367, "ARAF": 369, "AREG": 374, "ARF1": 375, "ARFRP1": 10139, "ARHGAP22": 58504, "ARHGAP26": 23092, "ARHGEF2": 9181, "ARID1B": 57492, "ARID2": 196528, "ARID5B": 84159, "ARMC10": 83787, "ARNT": 405, "ASAP1": 50807, "ASH1L": 55870, "ASPH": 444, "ASPSCR1": 79058, "ASS1": 445, "ASXL1": 171023, "ASXL2": 55252, "ATAD2": 29028, "ATF1": 466, "ATF7IP": 55729, "ATG4B": 23192, "ATG7": 10533, "ATIC": 471, "ATN1": 1822, "ATP10B": 23120, "ATP13A4": 84239, "ATP1B1": 481, "ATP2A2": 488, "ATP7B": 540, "ATRIP": 84126, "ATXN1": 6310, "AURKA": 6790, "AURKB": 9212, "AURKC": 6795, "AUTS2": 26053, "AXIN1": 8312, "AXIN2": 8313, "AXL": 558, "B2M": 567, "B4GALNT1": 2583, "BACH1": 571, "BAD": 572, "BAG4": 9530, "BAIAP2L1": 55971, "BAK1": 578, "BAP1": 8314, "BAX": 581, "BAZ2A": 11176, "BBC3": 27113, "BCAM": 4059, "BCAN": 63827, "BCAR4": 400500, "BCL10": 8915, "BCL11B": 64919, "BCL2": 596, "BCL2A1": 597, "BCL2L1": 598, "BCL2L11": 10018, "BCL2L2": 599, "BCL6": 604, "BCL9": 607, "BCOR": 54880, "BCORL1": 63035, "BCR": 613, "BEND2": 139105, "BFSP2": 8419, "BICC1": 80114, "BID": 637, "BIRC2": 329, "BIRC3": 330, "BIRC5": 332, "BIRC7": 79444, "BLM": 641, "BMI1": 648, "BMP4": 652, "BMPR1A": 657, "BMPR1B": 658, "BOC": 91653, "BORCS5": 118426, "BRCA1": 672, "BRCA2": 675, "BRD2": 6046, "BRD3": 8019, "BRD4": 23476, "BRDT": 676, "BRINP3": 339479, "BST2": 684, "BTBD1": 53339, "BTBD2": 55643, "BTD": 686, "BTF3L4": 91408, "BTG1": 694, "BTK": 695, "BTLA": 151888, "BTN3A1": 11119, "BTRC": 8945, "BUB1B": 701, "CA6": 765, "CA9": 768, "CACNA1S": 779, "CAD": 790, "CALCR": 799, "CALR": 811, "CAMTA1": 23261, "CAPZA2": 830, "CARD11": 84433, "CARM1": 10498, "CARMIL2": 146206, "CARS1": 833, "CASP6": 839, "CASP7": 840, "CASP8": 841, "CASQ2": 845, "CAT": 847, "CATSPERZ": 25858, "CAV1": 857, "CBFA2T3": 863, "CBFB": 865, "CBLB": 868, "CBLC": 23624, "CCAR2": 57805, "CCDC170": 80129, "CCDC186": 55088, "CCDC6": 8030, "CCDC88A": 55704, "CCDC91": 55297, "CCN2": 1490, "CCN6": 8838, "CCNA1": 8900, "CCNA2": 890, "CCNB1": 891, "CCNB2": 9133, "CCNB3": 85417, "CCNC": 892, "CCND1": 595, "CCND2": 894, "CCND3": 896, "CCNE1": 898, "CCNE2": 9134, "CCNF": 899, "CCNG1": 900, "CCNG2": 901, "CCNH": 902, "CCNI": 10983, "CCNI2": 645121, "CCNJ": 54619, "CCNK": 8812, "CCNL1": 57018, "CCNL2": 81669, "CCNO": 10309, "CCNT1": 904, "CCNT2": 905, "CCNY": 219771, "CCR2": 729230, "CCR4": 1233, "CCR5": 1234, "CCT2": 10576, "CD19": 930, "CD22": 933, "CD24": 100133941, "CD27": 939, "CD274": 29126, "CD276": 80381, "CD28": 940, "CD33": 945, "CD37": 951, "CD38": 952, "CD4": 920, "CD40": 958, "CD44": 960, "CD47": 961, "CD5": 921, "CD58": 965, "CD63": 967, "CD70": 970, "CD74": 972, "CD79A": 973, "CD79B": 974, "CD83": 9308, "CD86": 942, "CD8A": 925, "CD8B": 926, "CDC42": 998, "CDC42BPA": 8476, "CDC42BPB": 9578, "CDC73": 79577, "CDCA7": 83879, "CDH1": 999, "CDH11": 1009, "CDH2": 1000, "CDH23": 64072, "CDH3": 1001, "CDH4": 1002, "CDH6": 1004, "CDK1": 983, "CDK10": 8558, "CDK11A": 728642, "CDK11B": 984, "CDK13": 8621, "CDK14": 5218, "CDK15": 65061, "CDK16": 5127, "CDK17": 5128, "CDK18": 5129, "CDK19": 23097, "CDK2": 1017, "CDK20": 23552, "CDK3": 1018, "CDK4": 1019, "CDK5": 1020, "CDK6": 1021, "CDK7": 1022, "CDK8": 1024, "CDK9": 1025, "CDKN1A": 1026, "CDKN1B": 1027, "CDKN2B": 1030, "CDKN2C": 1031, "CDX2": 1045, "CEACAM5": 1048, "CEACAM6": 4680, "CEBPA": 1050, "CEBPE": 1053, "CENPA": 1058, "CEP43": 11116, "CEP55": 55165, "CEP85L": 387119, "CEP89": 84902, "CFTR": 1080, "CHD1": 1105, "CHD2": 1106, "CHD4": 1108, "CHD7": 55636, "CHGA": 1113, "CHKA": 1119, "CHTOP": 26097, "CIC": 23152, "CIITA": 4261, "CIP2A": 57650, "CIRBP": 1153, "CIT": 11113, "CKB": 1152, "CKS1B": 1163, "CLCN6": 1185, "CLDN18": 51208, "CLEC12A": 160364, "CLIP1": 6249, "CLIP2": 7461, "CLK3": 1198, "CLTC": 1213, "CLTCL1": 8218, "CLU": 1191, "CNTNAP2": 26047, "CNTRL": 11064, "COL14A1": 7373, "COL18A1": 80781, "COL1A1": 1277, "COL3A1": 1281, "COMMD3": 23412, "COP1": 64326, "COQ8B": 79934, "COX7A2L": 9167, "CPSF6": 11052, "CRB3": 92359, "CREB1": 1385, "CREB3L1": 90993, "CREB3L2": 64764, "CREBBP": 1387, "CREM": 1390, "CRKL": 1399, "CRLF2": 64109, "CRP": 1401, "CRTC1": 23373, "CRTC2": 200186, "CRTC3": 64784, "CSF1R": 1436, "CSMD1": 64478, "CSMD3": 114788, "CSNK1A1": 1452, "CSNK2A1": 1457, "CSTF3": 1479, "CTAG1A": 246100, "CTAG1B": 1485, "CTAG2": 30848, "CTBP2": 1488, "CTCF": 10664, "CTLA4": 1493, "CTNNA1": 1495, "CTNNA2": 1496, "CTNNA3": 29119, "CTNNBL1": 56259, "CTNND1": 1500, "CTRC": 11330, "CUL1": 8454, "CUL3": 8452, "CUX1": 1523, "CX3CR1": 1524, "CXCL1": 2919, "CXCL11": 6373, "CXCL13": 10563, "CXCL8": 3576, "CXCR4": 7852, "CYLD": 1540, "CYP17A1": 1586, "CYP19A1": 1588, "CYP2D6": 1565, "CYSLTR2": 57105, "DAB2": 1601, "DAB2IP": 153090, "DALRD3": 55152, "DAPK3": 1613, "DAXX": 1616, "DAZAP1": 26528, "DCC": 1630, "DCTN1": 1639, "DCUN1D1": 54165, "DDIT3": 1649, "DDIT4": 54541, "DDR1": 780, "DDR2": 4921, "DDX11": 1663, "DDX21": 9188, "DDX3X": 1654, "DDX41": 51428, "DEK": 7913, "DEPDC5": 9681, "DEPTOR": 64798, "DHODH": 1723, "DHX15": 1665, "DHX9": 1660, "DICER1": 23405, "DIP2C": 22982, "DIS3": 22894, "DIS3L2": 129563, "DKK1": 22943, "DLC1": 10395, "DLG1": 1739, "DLG5": 9231, "DLL3": 10683, "DLL4": 54567, "DNAJB1": 3337, "DNAJC21": 134218, "DNM3": 26052, "DNMT1": 1786, "DNMT3B": 1789, "DOCK4": 9732, "DOT1L": 84444, "DPH3": 285381, "DPP4": 1803, "DPYD": 1806, "DROSHA": 29102, "DSPP": 1834, "DTL": 51514, "DTX1": 1840, "DTX3L": 151636, "DUSP22": 56940, "DUX4": 100288687, "DYNC1I2": 1781, "DYRK1A": 1859, "DYRK1B": 9149, "DYRK4": 8798, "DYSF": 8291, "E2F1": 1869, "E2F3": 1871, "EBF1": 1879, "EDNRB": 1910, "EED": 8726, "EFNA4": 1945, "EGF": 1950, "EGFL7": 51162, "EGFR": 1956, "EGR1": 1958, "EHBP1": 23301, "EHMT2": 10919, "EIF1AX": 1964, "EIF3E": 3646, "EIF4A2": 1974, "EIF4E": 1977, "ELAVL1": 1994, "ELAVL3": 1995, "ELF1": 1997, "ELF3": 1999, "ELF4": 2000, "ELL": 8178, "ELN": 2006, "ELOC": 6921, "EMC2": 9694, "EMSY": 56946, "ENG": 2022, "ENPP3": 5169, "ENTPD1": 953, "EP300": 2033, "EPAS1": 2034, "EPCAM": 4072, "EPHA10": 284656, "EPHA2": 1969, "EPHA3": 2042, "EPHA4": 2043, "EPHA5": 2044, "EPHA7": 2045, "EPHA8": 2046, "EPHB1": 2047, "EPHB2": 2048, "EPHB4": 2050, "EPHB6": 2051, "EPOP": 100170841, "EPOR": 2057, "EPPK1": 83481, "EPS15": 2060, "ERBB2": 2064, "ERBB3": 2065, "ERBB4": 2066, "ERC1": 23085, "ERCC1": 2067, "ERCC2": 2068, "ERCC3": 2071, "ERCC4": 2072, "ERCC5": 2073, "ERCC6": 2074, "EREG": 2069, "ERF": 2077, "ERG": 2078, "ERLEC1": 27248, "ERLIN2": 11160, "ERN1": 2081, "ERRFI1": 54206, "ESR1": 2099, "ESR2": 2100, "ESRP1": 54845, "ESRRA": 2101, "ETFA": 2108, "ETNK1": 55500, "ETS1": 2113, "ETS2": 2114, "ETV1": 2115, "ETV4": 2118, "ETV5": 2119, "ETV6": 2120, "EWSR1": 2130, "EXO1": 9156, "EYA2": 2139, "EZH1": 2145, "EZH2": 2146, "EZR": 7430, "F3": 2152, "FADD": 8772, "FAH": 2184, "FAM114A2": 10827, "FAM118B": 79607, "FAM131B": 9715, "FAM133B": 257415, "FAM166A": 401565, "FAM174A": 345757, "FAM76A": 199870, "FAN1": 22909, "FANCB": 2187, "FANCC": 2176, "FANCD2": 2177, "FANCE": 2178, "FANCF": 2188, "FANCG": 2189, "FANCI": 55215, "FANCM": 57697, "FAP": 2191, "FAS": 355, "FASN": 2194, "FAT1": 2195, "FAT3": 120114, "FAT4": 79633, "FBXO2": 26232, "FBXO4": 26272, "FCER2": 2208, "FCGR1A": 2209, "FCHSD1": 89848, "FEN1": 2237, "FER1L5": 90342, "FES": 2242, "FEV": 54738, "FGF1": 2246, "FGF10": 2255, "FGF14": 2259, "FGF19": 9965, "FGF2": 2247, "FGF23": 8074, "FGF3": 2248, "FGF4": 2249, "FGF5": 2250, "FGF6": 2251, "FGF7": 2252, "FGF8": 2253, "FGF9": 2254, "FGFR1OP2": 26127, "FGFR4": 2264, "FGR": 2268, "FH": 2271, "FHL2": 2274, "FIP1L1": 81608, "FKBP15": 23307, "FLCN": 201163, "FLI1": 2313, "FLNC": 2318, "FLT1": 2321, "FLT4": 2324, "FMO4": 2329, "FN1": 2335, "FOLH1": 2346, "FOLR1": 2348, "FOSB": 2354, "FOXA1": 3169, "FOXJ2": 55810, "FOXL2": 668, "FOXM1": 2305, "FOXO1": 2308, "FOXO3": 2309, "FOXO4": 4303, "FOXP1": 27086, "FRK": 2444, "FRMD4A": 55691, "FRS2": 10818, "FSIP2": 401024, "FUBP1": 8880, "FUS": 2521, "FXR1": 8087, "FYB1": 2533, "FYN": 2534, "FZR1": 51343, "G3BP1": 10146, "GAA": 2548, "GAB1": 2549, "GAB2": 9846, "GABRA6": 2559, "GAS7": 8522, "GATA1": 2623, "GATA2": 2624, "GATA3": 2625, "GATA4": 2626, "GATA6": 2627, "GATM": 2628, "GCC2": 9648, "GCNT3": 9245, "GEN1": 348654, "GHR": 2690, "GID4": 79018, "GKAP1": 80318, "GLI1": 2735, "GLI2": 2736, "GLI3": 2737, "GLIS1": 148979, "GLIS2": 84662, "GLIS3": 169792, "GNA11": 2767, "GNA13": 10672, "GNAI1": 2770, "GNAO1": 2775, "GNAQ": 2776, "GNAS": 2778, "GNB1": 2782, "GNG2": 54331, "GNMT": 27232, "GNRHR": 2798, "GOLGA4": 2803, "GOLGA5": 9950, "GOLGB1": 2804, "GOPC": 57120, "GOT1": 2805, "GPBP1": 65056, "GPBP1L1": 60313, "GPC3": 2719, "GPNMB": 10457, "GPR107": 57720, "GPR161": 23432, "GPR20": 2843, "GPR32": 2854, "GPRIN2": 9721, "GPS2": 2874, "GREB1": 9687, "GREM1": 26585, "GRIN2A": 2903, "GRIN2B": 2904, "GRIPAP1": 56850, "GRM3": 2913, "GSDME": 1687, "GSK3B": 2932, "GTF2I": 2969, "GUCY2C": 2984, "GYG1": 2992, "H1-2": 3006, "H2AX": 3014, "H2BC4": 8347, "H2BC5": 3017, "H3-3A": 3020, "H3-3B": 3021, "H3-4": 8290, "H3-5": 440093, "H3C1": 8350, "H3C10": 8357, "H3C11": 8354, "H3C12": 8356, "H3C13": 653604, "H3C14": 126961, "H3C15": 333932, "H3C2": 8358, "H3C3": 8352, "H3C4": 8351, "H3C6": 8353, "H3C7": 8968, "H3C8": 8355, "HACL1": 26061, "HAUS5": 23354, "HAVCR1": 26762, "HBEGF": 1839, "HCFC1R1": 54985, "HCK": 3055, "HDAC1": 3065, "HDAC2": 3066, "HDAC3": 8841, "HDAC5": 10014, "HDAC6": 10013, "HDAC9": 9734, "HERPUD1": 9709, "HES1": 3280, "HES5": 388585, "HEY1": 23462, "HEY2": 23493, "HFE": 3077, "HGF": 3082, "HHAT": 55733, "HIF1A": 3091, "HIKESHI": 51501, "HIP1": 3092, "HLA-A": 3105, "HLA-B": 3106, "HLA-C": 3107, "HLA-DRB1": 3123, "HMCN1": 83872, "HMGA2": 8091, "HMGN2P46": 283651, "HNF1A": 6927, "HNF4G": 3174, "HNRNPA2B1": 3181, "HNRNPH1": 3187, "HNRNPK": 3190, "HNRNPUL1": 11100, "HOOK3": 84376, "HOXA10": 3206, "HOXA9": 3205, "HOXB13": 10481, "HOXD13": 3239, "HPCAL1": 3241, "HRD": 999999994, "HRG": 3273, "HSBP1": 3281, "HSD3B1": 3283, "HSF1": 3297, "HSF2": 3298, "HSF4": 3299, "HSP90AA1": 3320, "HSP90AB1": 3326, "HSPA5": 3309, "HSPB1": 3315, "HTRA1": 5654, "HTT": 3064, "HVCN1": 84329, "ICA1L": 130026, "ICAM1": 3383, "ICOSLG": 23308, "ID1": 3397, "ID2": 3398, "ID3": 3399, "ID4": 3400, "IDO1": 3620, "IFIT1": 3434, "IFIT1B": 439996, "IFIT2": 3433, "IFIT3": 3437, "IFNGR1": 3459, "IGF1": 3479, "IGF1R": 3480, "IGF2": 3481, "IGF2BP3": 10643, "IGFBP1": 3484, "IGFBP2": 3485, "IGFBP5": 3488, "IGFBP7": 3490, "IGH": 3492, "IGHV3-21": 28444, "IGHV4-34": 28395, "IGLL5": 100423062, "IKBKB": 3551, "IKBKE": 9641, "IKZF1": 10320, "IKZF3": 22806, "IL10": 3586, "IL13RA2": 3598, "IL2RA": 3559, "IL2RB": 3560, "IL3RA": 3563, "IL6": 3569, "IL6R": 3570, "IL7R": 3575, "INA": 9118, "ING3": 54556, "INHA": 3623, "INHBA": 3624, "INO80C": 125476, "INO80D": 54891, "INPP4A": 3631, "INPP4B": 8821, "INSR": 3643, "INTS8": 55656, "IPO7": 10527, "IRAK1": 3654, "IRAK4": 51135, "IRF1": 3659, "IRF2": 3660, "IRF2BP2": 359948, "IRF4": 3662, "IRF8": 3394, "IRS1": 3667, "IRS2": 8660, "IRS4": 8471, "ITGA5": 3678, "ITGAV": 3685, "ITGB3": 3690, "ITGB6": 3694, "ITK": 3702, "ITPKB": 3707, "ITPR2": 3709, "JAK1": 3716, "JAZF1": 221895, "JMJD1C": 221037, "JMJD6": 23210, "JUN": 3725, "KANK1": 23189, "KANK2": 25959, "KANK4": 163782, "KAT6A": 7994, "KAT7": 11143, "KCNH2": 3757, "KCNQ2": 3785, "KCTD7": 154881, "KDELR2": 11014, "KDM1A": 23028, "KDM1B": 221656, "KDM2A": 22992, "KDM2B": 84678, "KDM3A": 55818, "KDM3B": 51780, "KDM4A": 9682, "KDM4B": 23030, "KDM4C": 23081, "KDM4D": 55693, "KDM5A": 5927, "KDM5B": 10765, "KDM5C": 8242, "KDM6A": 7403, "KDM6B": 23135, "KDM7A": 80853, "KDR": 3791, "KEAP1": 9817, "KEL": 3792, "KHDRBS1": 10657, "KIAA1217": 56243, "KIAA1549": 57670, "KIDINS220": 57498, "KIF11": 3832, "KIF13B": 23303, "KIF2C": 11004, "KIF5B": 3799, "KIR2DL1": 3802, "KIR3DL2": 3812, "KLB": 152831, "KLC1": 3831, "KLF17": 128209, "KLF2": 10365, "KLF3": 51274, "KLF4": 9314, "KLF5": 688, "KLHL6": 89857, "KLHL7": 55975, "KLK2": 3817, "KMT2B": 9757, "KMT2C": 58508, "KMT2D": 8085, "KNSTRN": 90417, "KPNA3": 3839, "KRAS": 3845, "KTN1": 3895, "L3MBTL2": 83746, "LAG3": 3902, "LAMP1": 3916, "LAMTOR1": 55004, "LARP4B": 23185, "LATS1": 9113, "LATS2": 26524, "LCK": 3932, "LDLR": 3949, "LEO1": 123169, "LIFR": 3977, "LIG4": 3981, "LIMA1": 51474, "LIN28A": 79727, "LINC01210": 100507274, "LLGL2": 3993, "LMNA": 4000, "LMO1": 4004, "LOC389473": 389473, "LOXL2": 4017, "LRFN4": 78999, "LRIG1": 26018, "LRIG2": 9860, "LRIG3": 121227, "LRP1B": 53353, "LRRC1": 55227, "LRRC71": 149499, "LRRFIP1": 9208, "LRRTM4": 80059, "LSM14A": 26065, "LTK": 4058, "LY75": 4065, "LYN": 4067, "LYPD3": 27076, "LYSMD3": 116068, "LZTR1": 8216, "MACF1": 23499, "MAD1L1": 8379, "MAGEA1": 4100, "MAGEA3": 4102, "MAGEA4": 4103, "MAGEA6": 4105, "MAGEC1": 9947, "MAGI2": 9863, "MAGI3": 260425, "MALAT1": 378938, "MALT1": 10892, "MAML2": 84441, "MAML3": 55534, "MAMLD1": 10046, "MAP2K2": 5605, "MAP2K4": 6416, "MAP2K7": 5609, "MAP3K1": 4214, "MAP3K10": 4294, "MAP3K13": 9175, "MAP3K14": 9020, "MAP3K3": 4215, "MAP3K4": 4216, "MAP3K5": 4217, "MAP3K8": 1326, "MAP3K9": 4293, "MAP4K1": 11184, "MAP7D2": 256714, "MAPK1": 5594, "MAPK11": 5600, "MAPK14": 1432, "MAPK3": 5595, "MAPK6": 5597, "MAPK7": 5598, "MAPK8": 5599, "MAPK9": 5601, "MAPKAPK2": 9261, "MAPRE1": 22919, "MAST1": 22983, "MAST2": 23139, "MAX": 4149, "MBD4": 8930, "MBIP": 51562, "MBNL1": 4154, "MCL1": 4170, "MCM10": 55388, "MDC1": 9656, "MDK": 4192, "MDM2": 4193, "MDM4": 4194, "MDS2": 259283, "MECOM": 2122, "MED12": 9968, "MED15": 51586, "MED17": 9440, "MED23": 9439, "MEF2B": 100271849, "MEF2D": 4209, "MELK": 9833, "MEN1": 4221, "MERTK": 10461, "MET": 4233, "MFSD5": 84975, "MGA": 23269, "MGAM": 8972, "MGMT": 4255, "MIR548F1": 100302192, "MITF": 4286, "MKI67": 4288, "MKRN1": 23608, "MLANA": 2315, "MLH3": 27030, "MLLT1": 4298, "MLLT10": 8028, "MLLT3": 4300, "MME": 4311, "MMP14": 4323, "MMP2": 4313, "MMP9": 4318, "MN1": 4330, "MORC2": 22880, "MOS": 4342, "MPL": 4352, "MPRIP": 23164, "MRAS": 22808, "MRE11": 4361, "MRTFB": 57496, "MS4A1": 931, "MSH2": 4436, "MSH3": 4437, "MSI": 999999992, "MSLN": 10232, "MSMB": 4477, "MSN": 4478, "MST1": 4485, "MST1R": 4486, "MT-CO2": 4513, "MTA3": 57504, "MTAP": 4507, "MTOR": 2475, "MUC16": 94025, "MUC17": 140453, "MUC4": 4585, "MUC5AC": 4586, "MUC5B": 727897, "MUSK": 4593, "MUTYH": 4595, "MXD1": 4084, "MXD4": 10608, "MXI1": 4601, "MYB": 4602, "MYBL1": 4603, "MYC": 4609, "MYCL": 4610, "MYCN": 4613, "MYD88": 4615, "MYH10": 4628, "MYH11": 4629, "MYH13": 8735, "MYH15": 22989, "MYH9": 4627, "MYO18A": 399687, "MYO1F": 4542, "MYO5A": 4644, "MYOD1": 4654, "MYRIP": 25924, "MYT1L": 23040, "MZT1": 440145, "NAB2": 4665, "NACC2": 138151, "NADK": 65220, "NAMPT": 10135, "NAPRT": 93100, "NBN": 4683, "NCAM1": 4684, "NCL": 4691, "NCOA1": 8648, "NCOA2": 10499, "NCOA3": 8202, "NCOA4": 8031, "NCOR1": 9611, "NCR3LG1": 374383, "NDEL1": 81565, "NDRG1": 10397, "NECTIN1": 5818, "NECTIN2": 5819, "NECTIN4": 81607, "NEGR1": 257194, "NEK10": 152110, "NEK11": 79858, "NEK8": 284086, "NF1": 4763, "NF2": 4771, "NFASC": 23114, "NFATC1": 4772, "NFATC2": 4773, "NFATC3": 4775, "NFE2L2": 4780, "NFIA": 4774, "NFIB": 4781, "NFIX": 4784, "NFKB1": 4790, "NFKB2": 4791, "NFKBIA": 4792, "NFKBIE": 4794, "NFYC": 4802, "NISCH": 11188, "NKAIN2": 154215, "NKAIN4": 128414, "NKX2-1": 7080, "NKX3-1": 4824, "NONO": 4841, "NOP2": 4839, "NOS2": 4843, "NOTCH1": 4851, "NOTCH2": 4853, "NOTCH3": 4854, "NOTCH4": 4855, "NPAP1": 23742, "NPM1": 4869, "NPRL2": 10641, "NPRL3": 8131, "NQO1": 1728, "NR0B2": 8431, "NR3C1": 2908, "NR4A1": 3164, "NR4A3": 8013, "NRAP": 4892, "NRBF2": 29982, "NRF1": 4899, "NRG1": 3084, "NRG4": 145957, "NSD1": 64324, "NSD2": 7468, "NSD3": 54904, "NSMAF": 8439, "NT5C2": 22978, "NT5E": 4907, "NTRK1": 4914, "NTRK2": 4915, "NTRK3": 4916, "NUAK1": 9891, "NUAK2": 81788, "NUB1": 51667, "NUDCD3": 23386, "NUDT3": 11165, "NUFIP2": 57532, "NUGGC": 389643, "NUMA1": 4926, "NUMBL": 9253, "NUP214": 8021, "NUP93": 9688, "NUP98": 4928, "NUTM1": 256646, "NUTM2A": 728118, "NUTM2B": 729262, "NUTM2E": 283008, "NUTM2G": 441457, "ODC1": 4953, "OFD1": 8481, "OGA": 10724, "OGG1": 4968, "OGT": 8473, "OLFM4": 10562, "OPN4": 94233, "OPTN": 10133, "OSBPL1A": 114876, "OSBPL3": 26031, "PABPC4": 8761, "PACSIN2": 11252, "PAG1": 55824, "PAK1": 5058, "PAK3": 5063, "PAK4": 10298, "PAK5": 57144, "PAN3": 255967, "PAPSS1": 9061, "PARP1": 142, "PARP2": 10038, "PARP6": 56965, "PATZ1": 23598, "PAWR": 5074, "PAX3": 5077, "PAX5": 5079, "PAX7": 5081, "PAX8": 7849, "PAXIP1": 22976, "PBK": 55872, "PBRM1": 55193, "PBX1": 5087, "PCBP1": 5093, "PCBP2": 5094, "PCDH11X": 27328, "PCDH7": 5099, "PCLO": 27445, "PCM1": 5108, "PCMTD1": 115294, "PCNA": 5111, "PDCD1": 5133, "PDCD10": 11235, "PDCD1LG2": 80380, "PDCD4": 27250, "PDE10A": 10846, "PDE3A": 5139, "PDE4D": 5144, "PDE4DIP": 9659, "PDGFA": 5154, "PDGFB": 5155, "PDGFRA": 5156, "PDGFRB": 5159, "PDK1": 5163, "PDPK1": 5170, "PDS5B": 23047, "PDZRN3": 23024, "PER1": 5187, "PFN2": 5217, "PGR": 5241, "PHF1": 5252, "PHF19": 26147, "PHF20": 51230, "PHF5A": 84844, "PHF6": 84295, "PHGDH": 26227, "PHOX2B": 8929, "PICALM": 8301, "PIEZO1": 9780, "PIGA": 5277, "PIK3AP1": 118788, "PIK3C2B": 5287, "PIK3C2G": 5288, "PIK3C3": 5289, "PIK3CB": 5291, "PIK3CD": 5293, "PIK3CG": 5294, "PIK3IP1": 113791, "PIK3R1": 5295, "PIK3R2": 5296, "PIK3R3": 8503, "PIK3R5": 23533, "PIM1": 5292, "PIM2": 11040, "PIM3": 415116, "PIP4K2C": 79837, "PIWIL1": 9271, "PJA2": 9867, "PKM": 5315, "PKN1": 5585, "PLA2G15": 23659, "PLAG1": 5324, "PLCB4": 5332, "PLCG1": 5335, "PLCG2": 5336, "PLEKHA6": 22874, "PLEKHA7": 144100, "PLEKHF1": 79156, "PLEKHS1": 79949, "PLIN3": 10226, "PLK1": 5347, "PLK2": 10769, "PMAIP1": 5366, "PML": 5371, "PMS1": 5378, "PMS2": 5395, "PNRC1": 10957, "POFUT1": 23509, "POLB": 5423, "POLD1": 5424, "POLD2": 5425, "POLD3": 10714, "POLD4": 57804, "POLE": 5426, "POLG": 5428, "POLI": 11201, "POLK": 51426, "POLQ": 10721, "POLR1D": 51082, "POLR2A": 5430, "POLR2B": 5431, "POMK": 84197, "POT1": 25913, "POU5F1": 5460, "PPARG": 5468, "PPARGC1A": 10891, "PPEF1": 5475, "PPFIBP1": 8496, "PPFIBP2": 8495, "PPHLN1": 51535, "PPL": 5493, "PPM1D": 8493, "PPP1CB": 5500, "PPP2R1A": 5518, "PPP2R1B": 5519, "PPP2R2A": 5520, "PPP6C": 5537, "PRAME": 23532, "PRCC": 5546, "PRDM1": 639, "PRDM14": 63978, "PRDM16": 63976, "PRDM2": 7799, "PRDM9": 56979, "PRDX1": 5052, "PREX2": 80243, "PRKAA1": 5562, "PRKAA2": 5563, "PRKACA": 5566, "PRKAR1A": 5573, "PRKAR1B": 5575, "PRKCA": 5578, "PRKCB": 5579, "PRKCD": 5580, "PRKCE": 5581, "PRKCG": 5582, "PRKCH": 5583, "PRKCI": 5584, "PRKCQ": 5588, "PRKCZ": 5590, "PRKDC": 5591, "PRKN": 5071, "PRLR": 5618, "PRMT1": 3276, "PRMT2": 3275, "PRMT3": 10196, "PRMT5": 10419, "PRMT6": 55170, "PROM1": 8842, "PRPF40B": 25766, "PRPF8": 10594, "PRR15L": 79170, "PRRX1": 5396, "PRSS1": 5644, "PRSS8": 5652, "PSCA": 8000, "PSMB5": 5693, "PTCH1": 5727, "PTCH2": 8643, "PTGS2": 5743, "PTK2": 5747, "PTK2B": 2185, "PTK6": 5753, "PTK7": 5754, "PTP4A1": 7803, "PTPN1": 5770, "PTPN11": 5781, "PTPRB": 5787, "PTPRD": 5789, "PTPRK": 5796, "PTPRR": 5801, "PTPRS": 5802, "PTPRT": 11122, "PTPRZ1": 5803, "PTTG1": 9232, "PURB": 5814, "PVT1": 5820, "PWWP2A": 114825, "PYCR3": 65263, "QKI": 9444, "RAB11FIP1": 80223, "RAB35": 11021, "RABGAP1L": 9910, "RABL3": 285282, "RAC1": 5879, "RAD17": 5884, "RAD18": 56852, "RAD21": 5885, "RAD50": 10111, "RAD51": 5888, "RAD51AP1": 10635, "RAD52": 5893, "RAD54B": 25788, "RAD54L2": 23132, "RAF1": 5894, "RALGAPA1": 253959, "RALGPS1": 9649, "RANBP2": 5903, "RARA": 5914, "RARS1": 5917, "RASA1": 5921, "RASA3": 22821, "RASGEF1A": 221002, "RASGRF1": 5923, "RASGRF2": 5924, "RASSF4": 83937, "RBBP8": 5932, "RBM10": 8241, "RBM47": 54502, "RBMS3": 27303, "RBPMS": 11030, "RCSD1": 92241, "RECQL4": 9401, "REL": 5966, "RELA": 5970, "RELCH": 57614, "RFC1": 5981, "RFC2": 5982, "RFC3": 5983, "RFC4": 5984, "RFC5": 5985, "RGS7": 6000, "RHEB": 6009, "RHOA": 387, "RHOB": 388, "RHOT1": 55288, "RICTOR": 253260, "RIT1": 6016, "RNASEH2B": 79621, "RNF11": 26994, "RNF130": 55819, "RNF213": 57674, "RNF217-AS1": 7955, "RNF43": 54894, "RNPC3": 55599, "ROBO1": 6091, "ROCK1": 6093, "ROPN1": 54763, "ROR1": 4919, "ROR2": 4920, "RPA1": 6117, "RPA2": 6118, "RPA3": 6119, "RPA4": 29935, "RPE65": 6121, "RPGR": 6103, "RPL11": 6135, "RPL5": 6125, "RPS15": 6209, "RPS6": 6194, "RPS6KA1": 6195, "RPS6KA4": 8986, "RPS6KA5": 9252, "RPS6KB1": 6198, "RPS6KB2": 6199, "RPS6KC1": 26750, "RPTOR": 57521, "RRAGA": 10670, "RRAGD": 58528, "RRAS2": 22800, "RREB1": 6239, "RSF1": 51773, "RSPO1": 284654, "RSPO2": 340419, "RSPO3": 84870, "RSPO4": 343637, "RTEL1": 51750, "RTL9": 57529, "RUFY1": 80230, "RUFY2": 55680, "RUNX1": 861, "RUNX1T1": 862, "RXRA": 6256, "RYBP": 23429, "RYR1": 6261, "S100A7": 6278, "S1PR2": 9294, "SAAL1": 113174, "SALL2": 6297, "SAMD4B": 55095, "SAR1A": 56681, "SARAF": 51669, "SCAPER": 49855, "SCGB1A1": 7356, "SCGB1C1": 147199, "SCYL3": 57147, "SDC1": 6382, "SDC4": 6385, "SDCBP": 6386, "SDHA": 6389, "SDHB": 6390, "SDHC": 6391, "SDHD": 6392, "SEC31A": 22872, "SEC61G": 23480, "SELE": 6401, "SEM1": 7979, "SEMA4D": 10507, "SEPTIN14": 346288, "SEPTIN3": 55964, "SEPTIN6": 23157, "SEPTIN7": 989, "SEPTIN9": 10801, "SERPINB3": 6317, "SERPINB4": 6318, "SERPINE1": 5054, "SET": 6418, "SETBP1": 26040, "SETD2": 29072, "SETD7": 80854, "SETDB1": 9869, "SF1": 7536, "SF3B1": 23451, "SFPQ": 6421, "SGK1": 6446, "SH2B3": 10019, "SH2D1A": 4068, "SH3GLB1": 51100, "SH3PXD2A": 9644, "SHH": 6469, "SHOC2": 8036, "SHQ1": 55164, "SHTN1": 57698, "SIRPA": 140885, "SIRT1": 23411, "SIRT6": 51548, "SKP2": 6502, "SLAMF7": 57823, "SLC12A1": 6557, "SLC12A2": 6558, "SLC12A7": 10723, "SLC16A1": 6566, "SLC16A3": 9123, "SLC16A7": 9194, "SLC34A2": 10568, "SLC38A3": 10991, "SLC3A2": 6520, "SLC44A1": 23446, "SLC44A4": 80736, "SLC45A3": 85414, "SLC66A1": 54896, "SLC7A11": 23657, "SLC9A3R1": 9368, "SLCO2A1": 6578, "SLFN11": 91607, "SLFN12": 55106, "SLIT2": 9353, "SLX4": 84464, "SMAD2": 4087, "SMAD3": 4088, "SMAD4": 4089, "SMARCA4": 6597, "SMARCA5": 8467, "SMARCB1": 6598, "SMARCC1": 6599, "SMARCD1": 6602, "SMARCE1": 6605, "SMC1A": 8243, "SMC3": 9126, "SMG6": 23293, "SMIM17": 147670, "SMO": 6608, "SMYD3": 64754, "SNCAIP": 9627, "SND1": 27044, "SNX2": 6643, "SOAT1": 6646, "SOCS1": 8651, "SORBS1": 10580, "SOS1": 6654, "SOX10": 6663, "SOX11": 6664, "SOX17": 64321, "SOX2": 6657, "SOX6": 55553, "SOX9": 6662, "SP1": 6667, "SP3": 6670, "SPA17": 53340, "SPAG9": 9043, "SPANXA1": 30014, "SPECC1L": 23384, "SPEN": 23013, "SPICE1": 152185, "SPINK1": 6690, "SPOP": 8405, "SPTA1": 6708, "SPTBN1": 6711, "SQSTM1": 8878, "SRC": 6714, "SRF": 6722, "SRGAP3": 9901, "SRP54": 6729, "SRRM5": 100170229, "SRSF2": 6427, "SS18": 6760, "SSBP1": 6742, "SSBP2": 23635, "SSRP1": 6749, "SSTR1": 6751, "SSTR2": 6752, "SSTR3": 6753, "SSTR4": 6754, "SSTR5": 6755, "SSX1": 6756, "SSX2": 6757, "SSX4": 6759, "ST7": 7982, "STAG1": 10274, "STAG2": 10735, "STAG3": 10734, "STARD3NL": 83930, "STAT1": 6772, "STAT2": 6773, "STAT3": 6774, "STAT4": 6775, "STAT5A": 6776, "STAT5B": 6777, "STAT6": 6778, "STIL": 6491, "STING1": 340061, "STK10": 6793, "STK11": 6794, "STK19": 8859, "STK26": 51765, "STK3": 6788, "STK32B": 55351, "STK33": 65975, "STK35": 140901, "STK40": 83931, "STRBP": 55342, "STRN": 6801, "STRN3": 29966, "STX11": 8676, "SUFU": 51684, "SUPT16H": 11198, "SUV39H1": 6839, "SUV39H2": 79723, "SUZ12": 23512, "SVIL": 6840, "SVOPL": 136306, "SYK": 6850, "SYN2": 6854, "SYNRG": 11276, "TACC1": 6867, "TACC2": 10579, "TACC3": 10460, "TACSTD2": 4070, "TADA2A": 6871, "TAF1": 6872, "TAF15": 8148, "TAL1": 6886, "TANK": 10010, "TARBP2": 6895, "TBC1D1": 23216, "TBC1D3G": 654341, "TBK1": 29110, "TBL1XR1": 79718, "TBP": 6908, "TBX3": 6926, "TBXT": 6862, "TCF12": 6938, "TCF3": 6929, "TCF7L2": 6934, "TEAD1": 7003, "TEAD2": 8463, "TEAD4": 7004, "TEK": 7010, "TENM4": 26011, "TENT5C": 54855, "TERC": 7012, "TERT": 7015, "TET1": 80312, "TF": 7018, "TFCP2": 7024, "TFE3": 7030, "TFEB": 7942, "TFG": 10342, "TFRC": 7037, "TGFA": 7039, "TGFB1": 7040, "TGFBR1": 7046, "TGFBR2": 7048, "THADA": 63892, "THAP4": 51078, "THBS1": 7057, "THRB": 7068, "TILs": 999999993, "TLE4": 7091, "TLE6": 79816, "TLR7": 51284, "TLR8": 51311, "TMB": 999999991, "TMEM106B": 54664, "TMEM126A": 84233, "TMEM127": 55654, "TMEM165": 55858, "TMEM30A": 55754, "TMEM53": 79639, "TMEM59": 9528, "TMEM82": 388595, "TMEM87A": 25963, "TMEM98": 26022, "TMPRSS2": 7113, "TNF": 7124, "TNFAIP3": 7128, "TNFRSF10B": 8795, "TNFRSF12A": 51330, "TNFRSF14": 8764, "TNFRSF17": 608, "TNFRSF18": 8784, "TNFRSF1B": 7133, "TNFRSF4": 7293, "TNFRSF8": 943, "TNFRSF9": 3604, "TNFSF4": 7292, "TNIP1": 10318, "TNIP2": 79155, "TNK2": 10188, "TNS1": 7145, "TNS3": 64759, "TOP1": 7150, "TOP2A": 7153, "TP63": 8626, "TP73": 7161, "TPBG": 7162, "TPM1": 7168, "TPM3": 7170, "TPM4": 7171, "TPR": 7175, "TPTE2": 93492, "TRAF1": 7185, "TRAF2": 7186, "TRAF3": 7187, "TRAF6": 7189, "TRAF7": 84231, "TRDN": 10345, "TREM1": 54210, "TREM2": 54209, "TRIB2": 28951, "TRIM11": 81559, "TRIM16": 10626, "TRIM24": 8805, "TRIM27": 5987, "TRIM33": 51592, "TRIM37": 4591, "TRIM4": 89122, "TRIM63": 84676, "TRIM8": 81603, "TRIO": 7204, "TRIP13": 9319, "TRPM2": 7226, "TRPS1": 7227, "TRPV6": 55503, "TSC1": 7248, "TSC2": 7249, "TSGA10": 80705, "TSHR": 7253, "TTC28": 23331, "TTC5": 91875, "TTK": 7272, "TTN": 7273, "TUBB2A": 7280, "TUSC3": 7991, "TXN": 7295, "TYK2": 7297, "TYR": 7299, "TYRO3": 7301, "TYRP1": 7306, "U2AF1": 7307, "U2AF2": 11338, "UBC": 7316, "UBE2H": 7328, "UBE2R2": 54926, "UBL3": 5412, "UBR5": 51366, "UBTF": 7343, "UGT1A1": 54658, "UNC13C": 440279, "USH2A": 7399, "USP33": 23032, "USP38": 84640, "USP42": 84132, "VAMP2": 6844, "VAV1": 7409, "VAV2": 7410, "VCL": 7414, "VDR": 7421, "VEGFA": 7422, "VEGFB": 7423, "VEGFC": 7424, "VEGFD": 2277, "VEZF1": 7716, "VGLL1": 51442, "VIM": 7431, "VKORC1L1": 154807, "VMP1": 81671, "VTCN1": 79679, "WAC": 51322, "WASF1": 8936, "WASF2": 10163, "WDCP": 80304, "WDHD1": 11169, "WDR11": 55717, "WEE1": 7465, "WNK1": 65125, "WNT1": 7471, "WNT7A": 7476, "WRN": 7486, "WT1": 7490, "WWC1": 23286, "WWP1": 11059, "WWTR1": 25937, "XIAP": 331, "XPO1": 7514, "XRCC1": 7515, "XRCC2": 7516, "XRCC3": 7517, "XRCC4": 7518, "XRCC5": 7520, "XRCC6": 2547, "YAP1": 10413, "YBX1": 4904, "YES1": 7525, "YPEL5": 51646, "YWHAE": 7531, "YY1": 7528, "ZBTB2": 57621, "ZBTB20": 26137, "ZBTB7A": 51341, "ZC3H7A": 29066, "ZC3H7B": 23264, "ZC3HAV1": 56829, "ZCCHC8": 55596, "ZEB2": 9839, "ZFHX3": 463, "ZFP36L1": 677, "ZFTA": 65998, "ZIC4": 84107, "ZKSCAN1": 7586, "ZKSCAN5": 23660, "ZMIZ1": 57178, "ZMYM1": 79830, "ZMYM2": 7750, "ZMYM3": 9203, "ZMYM4": 9202, "ZMYND19": 116225, "ZNF207": 7756, "ZNF217": 7764, "ZNF384": 171017, "ZNF444": 55311, "ZNF492": 57615, "ZNF532": 55205, "ZNF700": 90592, "ZNF703": 80139, "ZNF713": 349075, "ZNF750": 79755, "ZNF767P": 79970, "ZNF880": 400713, "ZNRF3": 84133, "ZRSR2": 8233, "ZSCAN30": 100101467}


from .source_result import Source

class CKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        if gene in gene_dict:
            gene_id = gene_dict[gene]
            url = f"https://ckb.jax.org/gene/show?geneId={gene_id}"

        self.set_html(links=[{"url": url, "text": "Go"}])


def parse_gene_html(input_file, out="D:/ckb.json"):
    import re 
    import json

    url_gene_re = re.compile("<a\s+href=\"(?P<url>[^\"]+)\"\s+class=\"[^\"]+\">[\s\n]+(?P<gene>[^\s\n]+)", re.IGNORECASE)
    gene_dict = {}
    with open(input_file) as genes_handle:
        for match in url_gene_re.findall(genes_handle.read()):
            url = match[0]
            gene_id = int(url[url.rfind("=")+1:])
            gene_dict[match[1]] = gene_id

    with open(out, 'w')  as out_handle:
        out_handle.write(json.dumps(gene_dict))
    
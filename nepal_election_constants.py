PARTIES ={
    "नेपाली काँग्रेस": {"eng_name": "Nepali Congress", "sign": "🌳"},
    "नेपाल कम्युनिष्ट पार्टी (एकीकृत मार्क्सवादी लेनिनवादी)": {"eng_name": "CPN UML", "sign": "☀️"},
    # "नेपाली कम्युनिष्ट पार्टी": {"eng_name": "Nepali Communist Party", "sign": "⭐️"},
    "राष्ट्रिय स्वतन्त्र पार्टी": {"eng_name": "Rastriya Swatantra Party", "sign": "🔔"},
    # "राष्ट्रिय प्रजातन्त्र पार्टी": {"eng_name": "Rastriya Prajatantra Party", "sign": "plow"},
    # "जनता समाजवादी पार्टी": {"eng_name": "Janta Samajwadi Party", "sign": "?"},
}

NEPALI_DIGITS = str.maketrans({
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
})

# Common Nepali number words -> digits (include a few spelling variants)
NEPALI_NUMBER_WORDS = {
    "शुन्य": "0", "शून्य": "0",
    "एक": "1",
    "दुइ": "2", "दुई": "2",
    "तिन": "3", "तीन": "3",
    "चार": "4",
    "पाच": "5", "पाँच": "5",
    "छ": "6",
    "सात": "7",
    "आठ": "8",
    "नौ": "9",
    "दश": "10", "दस": "10",
    "एघार": "11", "एघार्": "11",
    "बाह्र": "12", "बार्ह": "12", "बार्‍ह": "12",
}


DIRGHA_TO_HRASWA = {
    "ई": "इ",
    "ऊ": "उ",
    "ी": "ि",
    "ू": "ु",
}

# Some extra standardizations that reduce common noisy variants
EXTRA_NORMALIZATIONS = [
    # normalize "पास" -> "pass"
    ("पास", "pass"),

    # make common +2 variants converge (we still match many variants later anyway)
    ("प्लसटू", "प्लसटु"),
    ("पल्सटू", "प्लसटु"),
    ("पल्सटु", "प्लसटु"),
]

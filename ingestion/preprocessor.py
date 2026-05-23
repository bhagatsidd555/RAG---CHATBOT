import re
import unicodedata


def clean_text(text):

    text=unicodedata.normalize(
        "NFKC",
        text
    )

    text=re.sub(
r"[^\x20-\x7E\n]",
" ",
text
    )

    text=re.sub(
r"\s+",
" ",
text
    )

    text=re.sub(
r"\b\d+\b",
"",
text
    )

    return text.strip()
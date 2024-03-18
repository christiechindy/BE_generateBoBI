import fitz  # PyMuPDF
import re

def replace_ligatures(text):
    # Define a dictionary mapping ligatures to their respective replacements
    ligature_replacements = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "−": "-",
        "¨o": "o",
        "–": "-",
        "¨u": "u",
    }

    # Construct a regular expression pattern to match any ligature
    pattern = re.compile('|'.join(re.escape(ligature) for ligature in ligature_replacements.keys()))

    # Replace ligatures in the text using the dictionary
    replaced_text = pattern.sub(lambda match: ligature_replacements[match.group(0)], text)
    
    return replaced_text

def extract_text_with_mupdf(pdf_path, page_start, page_end):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(page_start, page_end):
        page = doc[page_num]
        text += replace_ligatures(page.get_text())

    return text

def extract_text_from_a_page(pdf_path, page_number):
    doc = fitz.open(pdf_path)

    page = doc[page_number]
    text = page.get_text()
    text = text.split("\n")
    textTmp = ""
    for t in text:
        if t.endswith("-"):
            textTmp += t[:-1]
        else:
            textTmp += (t + " ")

    return replace_ligatures(textTmp)
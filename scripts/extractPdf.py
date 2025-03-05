import fitz  # PyMuPDF
import os

pdf_path = "PDFs/ALN_Elon_Musks_Monopoly.pdf"
cache_dir = "cache/"
os.makedirs(cache_dir, exist_ok=True)

# Derive a cache file path, e.g., "cache/sample.pdf.txt"
pdf_name = os.path.basename(pdf_path)
text_cache_path = os.path.join(cache_dir, pdf_name + ".txt")

text = ""
if os.path.exists(text_cache_path):
    # If cache exists, read from it instead of re-extracting
    with open(text_cache_path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"Loaded cached text for {pdf_name}")
else:
    # Extract text from PDF
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        page_text = page.get_text()  # extract text from page
        all_text.append(page_text)
    text = "\f".join(all_text)  # join pages with form feed (optional)
    # Save to cache file
    with open(text_cache_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted text from {pdf_name} and saved to cache.")
import fitz  # PyMuPDF
import os

pdf_path = "PDFs/sample.pdf"
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

# Create a subfolder for the images
images_dir = os.path.join(cache_dir, f"{os.path.splitext(pdf_name)[0]}_images")
os.makedirs(images_dir, exist_ok=True)

# Extract images from PDF
doc = fitz.open(pdf_path)
image_count = 0
for page_num, page in enumerate(doc):
    # Get image list
    image_list = page.get_images()
    
    # No images found on this page
    if not image_list:
        continue
    
    for img_index, img in enumerate(image_list):
        xref = img[0]  # image reference
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]  # image extension
        
        # Create image filename: page{page_num}_img{img_index}.{image_ext}
        image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
        image_path = os.path.join(images_dir, image_filename)
        
        # Save the image
        with open(image_path, "wb") as img_file:
            img_file.write(image_bytes)
        
        image_count += 1

print(f"Extracted {image_count} images from {pdf_name} and saved to {images_dir}")
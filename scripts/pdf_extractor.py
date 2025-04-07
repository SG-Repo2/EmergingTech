import os
import argparse
import logging
import re
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pdf_extractor')

def join_broken_uppercase(text):
    """
    Iteratively join adjacent uppercase sequences that were split.
    For example, "BER KSHIR E" becomes "BERKSHIRE".
    """
    pattern = re.compile(r'\b([A-Z]+)\s+([A-Z]+)\b')
    prev_text = None
    while text != prev_text:
        prev_text = text
        text = pattern.sub(r'\1\2', text)
    return text

def clean_text(text):
    """
    Clean and reformat extracted text for better readability.
    
    This function:
      - Removes hyphenation at line breaks (e.g., "im-\nplemented" becomes "implemented").
      - Joins broken uppercase words using join_broken_uppercase.
      - Uses double-newlines as paragraph markers.
      - Replaces remaining newlines with a space and collapses multiple spaces.
      - Restores paragraph breaks.
    
    Args:
        text (str): Raw extracted text.
    
    Returns:
        str: Cleaned text.
    """
    # Remove hyphenation at line breaks
    text = re.sub(r'-\s*\n\s*', '', text)
    # Join broken uppercase words
    text = join_broken_uppercase(text)
    # Mark paragraph breaks
    text = text.replace("\n\n", "<PARA>")
    # Replace any remaining newlines with a space
    text = text.replace("\n", " ")
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
    # Restore paragraph breaks
    text = text.replace("<PARA>", "\n\n")
    return text.strip()

def extract_text(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: Extracted and cleaned text content.
    """
    logger.info(f"Extracting text from {pdf_path}")
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                raw_text = page.extract_text()
                text += raw_text + "\n\n"
        cleaned = clean_text(text)
        logger.info(f"Successfully extracted and cleaned text from {pdf_path}")
        return cleaned
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def save_text(text, output_path):
    """
    Save extracted text to a .txt file.
    
    Args:
        text (str): Extracted text content.
        output_path (str): Path to save the text file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
        logger.info(f"Text saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving text to {output_path}: {str(e)}")

def process_pdf(pdf_path, output_dir):
    """
    Process a single PDF file to extract text.
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory to save the output text file.
    """
    try:
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{pdf_name}_text.txt")
        text = extract_text(pdf_path)
        if text:
            save_text(text, output_path)
        logger.info(f"Successfully processed {pdf_path}")
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")

def process_directory(input_dir, output_dir):
    """
    Process all PDF files in a directory to extract text.
    
    Args:
        input_dir (str): Directory containing PDF files.
        output_dir (str): Directory to save output text files.
    """
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                 if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    for pdf_file in pdf_files:
        process_pdf(pdf_file, output_dir)

def main():
    """Main function to parse arguments and process PDFs."""
    parser = argparse.ArgumentParser(description='Extract and clean text from PDF files')
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', help='Path to a PDF file')
    input_group.add_argument('-d', '--directory', help='Path to a directory containing PDF files')
    
    parser.add_argument('-o', '--output', default='extracted_data',
                        help='Directory to save extracted text (default: ./extracted_data)')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    if args.file:
        if os.path.isfile(args.file) and args.file.lower().endswith('.pdf'):
            process_pdf(args.file, args.output)
        else:
            logger.error(f"Invalid PDF file: {args.file}")
    elif args.directory:
        if os.path.isdir(args.directory):
            process_directory(args.directory, args.output)
        else:
            logger.error(f"Invalid directory: {args.directory}")

if __name__ == "__main__":
    main()
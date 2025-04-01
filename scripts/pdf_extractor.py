import os
import argparse
import logging
import PyPDF2
import camelot
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pdf_extractor')

def extract_text(pdf_path):
    """
    Extract text content from a PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    logger.info(f"Extracting text from {pdf_path}")
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        logger.info(f"Successfully extracted text from {pdf_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def extract_tables(pdf_path, min_accuracy=80, stream_only_if_needed=True):
    """
    Extract tables from a PDF file using Camelot
    
    Args:
        pdf_path (str): Path to the PDF file
        min_accuracy (int): Minimum accuracy threshold for tables (0-100)
        stream_only_if_needed (bool): Only use stream if lattice finds no tables
        
    Returns:
        list: List of pandas DataFrames containing tables
    """
    logger.info(f"Extracting tables from {pdf_path}")
    tables = []
    try:
        # First try lattice mode (for bordered tables)
        lattice_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        lattice_found = False
        
        if lattice_tables.n > 0:
            for i, table in enumerate(lattice_tables):
                if table.df.size > 0 and table.accuracy > min_accuracy:  # Only include tables above threshold
                    lattice_found = True
                    tables.append((f"table_{i+1}", table.df))
                    logger.info(f"Found lattice table with accuracy {table.accuracy:.1f}%")
        
        # Only try stream mode if we didn't find good tables with lattice or if explicitly requested
        if (not lattice_found or not stream_only_if_needed):
            stream_tables = camelot.read_pdf(
                pdf_path, 
                pages='all', 
                flavor='stream',
                edge_tol=50,        # More tolerant edge detection
                row_tol=10,         # Stricter row tolerance
                column_tol=10       # Stricter column tolerance
            )
            
            if stream_tables.n > 0:
                for i, table in enumerate(stream_tables):
                    # More strict filtering for stream tables
                    if (table.df.size > 0 and 
                        table.accuracy > min_accuracy and
                        table.df.shape[0] > 1 and   # At least 2 rows
                        table.df.shape[1] > 1):     # At least 2 columns
                        tables.append((f"table_s{i+1}", table.df))
                        logger.info(f"Found stream table with accuracy {table.accuracy:.1f}%")
        
        logger.info(f"Found {len(tables)} qualifying tables in {pdf_path}")
        return tables
    except Exception as e:
        logger.error(f"Error extracting tables from {pdf_path}: {str(e)}")
        return []

def save_text(text, output_path):
    """
    Save extracted text to a file
    
    Args:
        text (str): Extracted text content
        output_path (str): Path to save the text file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
        logger.info(f"Text saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving text to {output_path}: {str(e)}")

def save_tables(tables, base_output_path):
    """
    Save extracted tables to CSV files
    
    Args:
        tables (list): List of (table_name, DataFrame) tuples
        base_output_path (str): Base path for saving CSV files
    """
    for table_name, df in tables:
        try:
            output_path = f"{base_output_path}_{table_name}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Table saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving table to {output_path}: {str(e)}")

def process_pdf(pdf_path, output_dir, skip_tables=False):
    """
    Process a single PDF file to extract text and tables
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save output files
        skip_tables (bool): If True, skip table extraction
    """
    try:
        # Create output filename based on PDF filename
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_base = os.path.join(output_dir, pdf_name)
        
        # Extract and save text
        text = extract_text(pdf_path)
        if text:
            text_output_path = f"{output_base}_text.txt"
            save_text(text, text_output_path)
        
        # Extract and save tables (if not skipped)
        if not skip_tables:
            tables = extract_tables(pdf_path)
            if tables:
                save_tables(tables, output_base)
            
        logger.info(f"Successfully processed {pdf_path}")
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")

def process_directory(input_dir, output_dir, skip_tables=False):
    """
    Process all PDF files in a directory
    
    Args:
        input_dir (str): Directory containing PDF files
        output_dir (str): Directory to save output files
        skip_tables (bool): If True, skip table extraction
    """
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    for pdf_file in pdf_files:
        process_pdf(pdf_file, output_dir, skip_tables)

def main():
    """Main function to parse arguments and process PDFs"""
    parser = argparse.ArgumentParser(description='Extract text and tables from PDF files')
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', help='Path to a PDF file')
    input_group.add_argument('-d', '--directory', help='Path to a directory containing PDF files')
    
    parser.add_argument('-o', '--output', default='extracted_data',
                        help='Directory to save extracted data (default: ./extracted_data)')
    parser.add_argument('--accuracy', type=int, default=80,
                        help='Minimum accuracy threshold for table detection (0-100)')
    parser.add_argument('--all-methods', action='store_true',
                        help='Always use both lattice and stream methods')
    parser.add_argument('--text-only', action='store_true',
                        help='Extract only text, skip table extraction')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    
    # Only set up table extraction if we're not skipping it
    if not args.text_only:
        # Update the global extract_tables function with command line parameters
        global extract_tables
        original_extract_tables = extract_tables
        
        def extract_tables_wrapper(pdf_path):
            return original_extract_tables(
                pdf_path, 
                min_accuracy=args.accuracy, 
                stream_only_if_needed=not args.all_methods
            )
        
        # Replace the function with our wrapper
        extract_tables = extract_tables_wrapper
    
    if args.file:
        if os.path.isfile(args.file) and args.file.lower().endswith('.pdf'):
            process_pdf(args.file, output_dir, skip_tables=args.text_only)
        else:
            logger.error(f"Invalid PDF file: {args.file}")
    elif args.directory:
        if os.path.isdir(args.directory):
            process_directory(args.directory, output_dir, skip_tables=args.text_only)
        else:
            logger.error(f"Invalid directory: {args.directory}")

if __name__ == "__main__":
    main()

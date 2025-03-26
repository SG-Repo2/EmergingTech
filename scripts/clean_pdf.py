import re
import os
import argparse

def clean_pdf_text(text):
    """
    Clean up text extracted from a PDF.
    
    Args:
        text (str): The raw extracted text from a PDF
        
    Returns:
        str: Cleaned text
    """
    # Remove date/time patterns (like "2/14/25, 9:54 AM")
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[APM]{2}', '', text)
    
    # Remove URL patterns
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove page numbers (like "1/16", "2/16")
    text = re.sub(r'\d+/\d+', '', text)
    
    # Remove redundant site headers (more aggressive pattern)
    text = re.sub(r"Nvidia's Christmas Present:.+?SemiAnalysis", '', text, flags=re.DOTALL)
    # Also remove any repeating header instances without the full pattern
    text = re.sub(r"Nvidia's Christmas Present: GB300 & B300 – Reasoning Inference, Amazon, Memory, Supply Chain", '', text)
    
    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove Reply lines (more robust)
    text = re.sub(r'^\s*Reply\s*$', '', text, flags=re.MULTILINE)
    
    # Remove "Source: SemiAnalysis" lines
    text = re.sub(r'Source:\s*SemiAnalysis', '', text)
    
    # Remove "Keep Reading" and "Next Article" sections
    text = re.sub(r'Next Article.+?Keep Reading', '', text, flags=re.DOTALL)
    
    # Remove "Comments" header but keep the comment content
    text = re.sub(r'^\s*Comments\s*$', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    
    # Additional whitespace cleanup
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Clean up text extracted from a PDF')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output_file', '-o', help='Path to the output file (default: input_file_clean.txt)')
    parser.add_argument('--remove_comments', '-c', action='store_true', 
                        help='Remove the entire comments section if present')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Determine output file path
    input_path = args.input_file
    if args.output_file:
        output_path = args.output_file
    else:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_clean.txt"
    
    # Read input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Clean the text
    cleaned_text = clean_pdf_text(text)
    
    # Optional: Remove comments section entirely
    if args.remove_comments and "Comments" in cleaned_text:
        comments_pos = cleaned_text.find("Comments")
        if comments_pos > 0:
            cleaned_text = cleaned_text[:comments_pos].strip()
            print("Comments section removed")
    
    # Write output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"Cleaned text saved to {output_path}")
    except Exception as e:
        print(f"Error writing file: {e}")
        return

if __name__ == "__main__":
    main()
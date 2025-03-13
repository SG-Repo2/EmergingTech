import json
import re
import argparse
from pathlib import Path

def clean_citations(text):
    """
    Clean citation references from text.
    Removes patterns like [oai_citation_attribution:123‡source.com](https://www.example.com)
    """
    if not text:
        return text
        
    # Pattern to match citation references with the format:
    # [oai_citation_attribution:number‡domain.com](URL)
    citation_pattern = r'\[oai_citation_attribution:[^\]]+\]\([^)]+\)'
    
    # Remove the citation references
    cleaned_text = re.sub(citation_pattern, '', text)
    
    # Clean up any double spaces that might have been created
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Trim whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def process_json_file(input_file, output_file=None):
    """
    Process a JSON file to clean citations from fields containing 'source' or 'context'.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to save the cleaned JSON (if None, will use input_file with '_cleaned' suffix)
    
    Returns:
        Path to the output file
    """
    # Determine output file path if not provided
    if not output_file:
        input_path = Path(input_file)
        output_file = input_path.with_stem(f"{input_path.stem}_cleaned")
    
    # Load the JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process the data based on its structure
    if isinstance(data, list):
        # If it's a list of items
        for item in data:
            process_item(item)
    elif isinstance(data, dict):
        # If it's a dictionary
        process_item(data)
    else:
        raise ValueError("JSON data must be either a list or dictionary")
    
    # Write the cleaned data to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return output_file

def process_item(item):
    """
    Process an individual item (dictionary) to clean citations from relevant fields.
    
    Args:
        item: Dictionary to process
    """
    if not isinstance(item, dict):
        return
    
    # Process each key in the dictionary
    for key, value in item.items():
        if isinstance(value, str):
            # If the key contains 'source' or 'context' or the value contains citation markers
            if ('source' in key.lower() or 
                'context' in key.lower() or 
                re.search(r'\[oai_citation_attribution:', value)):
                item[key] = clean_citations(value)
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            process_item(value)
        elif isinstance(value, list):
            # Process lists that might contain dictionaries
            for list_item in value:
                if isinstance(list_item, dict):
                    process_item(list_item)

def main():
    parser = argparse.ArgumentParser(description="Clean citation references from JSON files")
    parser.add_argument("input_file", help="Path to the input JSON file")
    parser.add_argument("-o", "--output", help="Path to save the cleaned JSON (optional)")
    args = parser.parse_args()
    
    output_file = process_json_file(args.input_file, args.output)
    print(f"Processed {args.input_file} and saved to {output_file}")

if __name__ == "__main__":
    main()
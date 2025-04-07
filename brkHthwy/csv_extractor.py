#!/usr/bin/env python3
"""
CSV Prediction Extractor

This module handles extraction and processing of CSV-formatted financial prediction data.
It processes raw text input containing prediction data and creates a properly formatted CSV file.

The CSV format includes columns for:
- Prediction: The forward-looking statement text
- Company: The organization making the prediction
- Industry: The relevant industry sector
- Source: Document or speaker source
- Context: Background information
- Timeline: Time horizon for the prediction
- Confidence: Certainty level (High, Moderate, Low)
- Stance: Outlook perspective (Bullish, Bearish, Neutral, Mixed)
- Supporting Factors: Elements supporting the prediction
- Potential Risks: Factors that could challenge the prediction
"""

import csv
import re

def extract_csv_data(csv_content, output_path):
    """
    Extract and process CSV prediction data from text content.
    
    Args:
        csv_content (str): Raw CSV section content
        output_path (str): Path where the CSV file will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Processing CSV content ({len(csv_content)} chars)")
        
        # Skip any commentary or explanatory text before the actual CSV
        # Look for the header line or data pattern
        csv_lines = []
        started = False
        found_header = False
        
        # First, try to find the header line
        lines = csv_content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for header pattern
            if "Prediction,Company,Industry" in line:
                found_header = True
                print("Found CSV header line")
                csv_lines = [line]  # Start with header
                # Add all subsequent lines that could be data
                for next_line in lines[i+1:]:
                    if next_line.strip() and not next_line.strip().startswith("Below is"):
                        csv_lines.append(next_line.strip())
                break
        
        # If header not found, look for data with quotes (typical CSV pattern)
        if not found_header:
            print("Header not found, looking for CSV data patterns")
            in_csv_section = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for marker lines indicating CSV data
                if "Below is a single table" in line or "CSV OUTPUT" in line:
                    in_csv_section = True
                    continue
                
                # Check for section boundaries
                if line.startswith("⸻") or line.startswith("---"):
                    if in_csv_section and csv_lines:  # If we already collected data, this is the end
                        break
                    in_csv_section = True  # This might be the start
                    continue
                
                # Collect data lines
                if in_csv_section and (line.count(',') >= 3 or line.startswith('"')):
                    csv_lines.append(line)
                    # If this looks like a header, note it
                    if "Prediction" in line and "Company" in line:
                        found_header = True
        
        if not csv_lines:
            print("No CSV data found using standard patterns")
            # Last resort: just take lines with commas that might be CSV data
            comma_lines = [line.strip() for line in lines if line.strip() and line.strip().count(',') >= 3]
            if comma_lines:
                print(f"Found {len(comma_lines)} lines with commas")
                csv_lines = comma_lines
        
        print(f"Extracted {len(csv_lines)} CSV lines")
        
        # Process the CSV data
        rows = []
        header = None
        
        for line in csv_lines:
            # Skip empty lines or commentary
            if not line.strip() or line.strip().startswith("Below is"):
                continue
                
            # Use the first line as header if not explicitly found
            if header is None:
                header = parse_csv_line(line)
                if "Prediction" in header:
                    found_header = True
                rows.append(header)
                continue
            
            # Parse the line while respecting quoted fields
            row = parse_csv_line(line)
            if row and len(row) > 0:
                # Make sure row has the same number of columns as header
                if len(row) < len(header):
                    row.extend([''] * (len(header) - len(row)))
                elif len(row) > len(header):
                    row = row[:len(header)]
                rows.append(row)
        
        if not rows:
            print("No valid CSV rows extracted")
            return False
            
        if len(rows) == 1 and not found_header:
            print("Only found one row and it's not a clear header")
            # Try to create a default header
            default_header = ["Prediction", "Company", "Industry", "Source", "Context", 
                             "Timeline", "Confidence", "Stance", "Supporting Factors", "Potential Risks"]
            if len(rows[0]) <= len(default_header):
                rows.insert(0, default_header[:len(rows[0])])
            else:
                # Create numbered columns for any extras
                header = default_header + [f"Column{i}" for i in range(len(default_header)+1, len(rows[0])+1)]
                rows.insert(0, header)
        
        # Write to CSV file
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in rows:
                writer.writerow(row)
        
        print(f"Wrote {len(rows)} rows to CSV file")
        return True
        
    except Exception as e:
        print(f"Error extracting CSV data: {e}")
        import traceback
        traceback.print_exc()
        return False

def parse_csv_line(line):
    """
    Parse a CSV line while correctly handling quoted fields that may contain commas.
    
    Args:
        line (str): A CSV line to parse
        
    Returns:
        list: The parsed fields from the line
    """
    fields = []
    field = ""
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
            field += char
        elif char == ',' and not in_quotes:
            fields.append(field.strip())
            field = ""
        else:
            field += char
    
    # Add the last field
    if field:
        fields.append(field.strip())
    
    return fields

def parse_csv_with_headers(csv_content):
    """
    Parse CSV content with support for headers and return structured data.
    
    Args:
        csv_content (str): Raw CSV data as string
        
    Returns:
        dict: {'headers': list, 'data': list of dictionaries}
    """
    lines = [line for line in csv_content.split('\n') if line.strip()]
    if not lines:
        return {'headers': [], 'data': []}
    
    # Parse header line
    headers = parse_csv_line(lines[0])
    
    # Parse data rows
    data = []
    for line in lines[1:]:
        if not line.strip():
            continue
            
        row_values = parse_csv_line(line)
        if len(row_values) < len(headers):
            # Pad with empty values if row is too short
            row_values.extend([''] * (len(headers) - len(row_values)))
        elif len(row_values) > len(headers):
            # Truncate if row is too long
            row_values = row_values[:len(headers)]
            
        row_dict = {headers[i]: row_values[i] for i in range(len(headers))}
        data.append(row_dict)
    
    return {'headers': headers, 'data': data}

# System prompt for CSV extraction
CSV_SYSTEM_PROMPT = """
You are an expert in financial document analysis, specializing in extracting forward-looking statements.
Your task is to identify predictions in financial texts and structure them in CSV format with these columns:

1. Prediction - Direct quote or paraphrase of the forward-looking statement
2. Company - Organization making the prediction ("Unknown" if unclear)
3. Industry - Relevant industry sector ("Unknown" if unclear)
4. Source - Document or speaker (e.g., CEO letter, CFO remarks)
5. Context - Brief reference to where statement appears + relevant background
6. Timeline - Short-term, Medium-term, Long-term, Conditional, Recurring, or Not specified
7. Confidence - High, Moderate, Low, or Not specified
8. Stance - Bullish, Bearish, Neutral, or Mixed
9. Supporting Factors - Key data justifying the forecast
10. Potential Risks - Factors that might derail or challenge the prediction

GUIDELINES:
- Extract only explicit or strongly implied forward-looking statements
- Exclude purely historical information or general aspirations lacking specificity
- Use "Unknown" where Company or Industry is not specified
- Preserve original quotes when possible for the Prediction field
- Evaluate timeline, confidence, and stance based on language used
- Include all relevant supporting factors and risks mentioned

OUTPUT FORMAT:
A clean CSV file with a header row followed by data rows containing the extracted predictions.
"""

# Action prompt for CSV extraction
CSV_ACTION_PROMPT = """
Analyze the provided financial text and extract all forward-looking statements.
Structure your findings in CSV format with these columns:
Prediction,Company,Industry,Source,Context,Timeline,Confidence,Stance,Supporting Factors,Potential Risks

For each forward-looking statement:
1. Start with the exact prediction text in quotes
2. Identify the company making the prediction
3. Determine the relevant industry
4. Note the source (person or document)
5. Provide brief context
6. Classify the timeline (Short-term, Medium-term, Long-term, Conditional, or Not specified)
7. Assess confidence level (High, Moderate, Low)
8. Determine stance (Bullish, Bearish, Neutral, Mixed)
9. List key supporting factors
10. Identify potential risks or challenges

Return ONLY the valid CSV output with no additional commentary.
"""

if __name__ == "__main__":
    # For testing as standalone module
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        extract_csv_data(content, "test_output.csv")
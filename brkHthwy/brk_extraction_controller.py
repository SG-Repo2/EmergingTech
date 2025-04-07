#!/usr/bin/env python3
"""
Berkshire Hathaway Financial Prediction Extraction Framework - Controller Script

This script acts as the main controller for processing financial documents and extracting
forward-looking statements in three output formats: CSV, JSON, and PDF Report.

Usage:
    python brk_extraction_controller.py <input_file>

Dependencies:
    - csv_extractor.py
    - json_extractor.py
    - report_generator.py
    - fpdf (for PDF generation)
"""

import os
import sys
import re
from datetime import datetime

# Check for necessary dependencies
try:
    from fpdf import FPDF
except ImportError:
    print("Error: Required dependency 'fpdf' not found.")
    print("Please install it using: pip install fpdf")
    sys.exit(1)

# Try to import the specialized extractors
# If any are missing, create basic implementations
try:
    from csv_extractor import extract_csv_data
except ImportError:
    print("Warning: csv_extractor.py not found, using basic implementation")
    def extract_csv_data(csv_content, output_path):
        """Basic CSV extraction implementation."""
        try:
            import csv
            lines = [line for line in csv_content.split('\n') if line.strip()]
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for line in lines:
                    if ',' in line:
                        writer.writerow([field.strip('"') for field in line.split(',')])
            return True
        except Exception as e:
            print(f"Error in basic CSV extraction: {e}")
            return False

try:
    from json_extractor import extract_json_data
except ImportError:
    print("Warning: json_extractor.py not found, using basic implementation")
    def extract_json_data(json_content, output_path):
        """Basic JSON extraction implementation."""
        try:
            import json
            # Find JSON-like content
            json_pattern = r'({[\s\S]*})'
            json_match = re.search(json_pattern, json_content)
            if json_match:
                json_str = json_match.group(1)
                # Try to parse and format
                json_data = json.loads(json_str)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error in basic JSON extraction: {e}")
            return False

try:
    from report_generator import generate_report
except ImportError:
    print("Warning: report_generator.py not found, using basic implementation")
    def generate_report(report_content, output_path):
        """Basic report generation implementation."""
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Financial Prediction Analysis Report", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", "", 12)
            
            # Split by paragraphs
            paragraphs = report_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    pdf.multi_cell(0, 10, para.strip())
                    pdf.ln(5)
            
            pdf.output(output_path)
            return True
        except Exception as e:
            print(f"Error in basic report generation: {e}")
            return False

def detect_input_format(content):
    """
    Analyze the input content to determine its format and structure.
    
    Args:
        content (str): The input text content
        
    Returns:
        dict: Dictionary with detected format details
    """
    format_info = {
        "has_csv_section": False,
        "has_json_section": False,
        "has_report_section": False,
        "sections": []
    }
    
    # Check for section markers
    if re.search(r'CSV OUTPUT|CSV\s+Output', content, re.IGNORECASE):
        format_info["has_csv_section"] = True
        format_info["sections"].append("csv")
    
    if re.search(r'JSON OUTPUT|JSON\s+Output', content, re.IGNORECASE):
        format_info["has_json_section"] = True
        format_info["sections"].append("json")
    
    if re.search(r'TEXTUAL REPORT|Report|Summary', content, re.IGNORECASE):
        format_info["has_report_section"] = True
        format_info["sections"].append("report")
    
    # Check for content patterns if no explicit markers found
    if not format_info["has_csv_section"]:
        if re.search(r'Prediction,Company,Industry', content):
            format_info["has_csv_section"] = True
            format_info["sections"].append("csv")
    
    if not format_info["has_json_section"]:
        if re.search(r'{\s*"nodes"\s*:', content, re.DOTALL):
            format_info["has_json_section"] = True
            format_info["sections"].append("json")
    
    if not format_info["has_report_section"]:
        if re.search(r'\([A-Z]\).*?Summary', content, re.DOTALL) or re.search(r'Summary of the Prediction', content):
            format_info["has_report_section"] = True
            format_info["sections"].append("report")
    
    # Check for section dividers
    format_info["section_dividers"] = []
    dividers = re.findall(r'(⸻|\-{3,}|={3,}|\*{3,})', content)
    if dividers:
        format_info["section_dividers"] = list(set(dividers))
    
    return format_info

def extract_sections(content, format_info):
    """
    Extract the separate sections from the content based on format detection.
    
    Args:
        content (str): The input text content
        format_info (dict): Format detection information
        
    Returns:
        dict: Dictionary with extracted section contents
    """
    sections = {}
    
    # If we have dividers, try to split by them
    if format_info["section_dividers"]:
        divider_pattern = '|'.join(re.escape(d) for d in format_info["section_dividers"])
        
        # Try to find numbered sections
        numbered_sections = re.split(f"({divider_pattern})\s*\d+\.\s+", content)
        
        if len(numbered_sections) > 1:
            # Process numbered sections
            for i in range(1, len(numbered_sections), 2):
                if i+1 < len(numbered_sections):
                    section_text = numbered_sections[i+1]
                    first_line = section_text.split('\n', 1)[0].strip().lower()
                    
                    if "csv" in first_line:
                        if '\n' in section_text:
                            sections["csv"] = section_text.split('\n', 1)[1].strip()
                        else:
                            sections["csv"] = section_text.strip()
                    elif "json" in first_line:
                        if '\n' in section_text:
                            sections["json"] = section_text.split('\n', 1)[1].strip()
                        else:
                            sections["json"] = section_text.strip()
                    elif "report" in first_line or "textual" in first_line:
                        if '\n' in section_text:
                            sections["report"] = section_text.split('\n', 1)[1].strip()
                        else:
                            sections["report"] = section_text.strip()
        else:
            # Try simple divider split
            simple_sections = re.split(f"({divider_pattern})", content)
            if len(simple_sections) > 1:
                for i, section in enumerate(simple_sections):
                    if section.strip():
                        if i == 1 or "csv" in section.lower():
                            sections["csv"] = section.strip()
                        elif i == 3 or "json" in section.lower():
                            sections["json"] = section.strip()
                        elif i == 5 or "report" in section.lower() or "textual" in section.lower():
                            sections["report"] = section.strip()
    
    # If we have specific sections identified but not extracted yet
    if format_info["has_csv_section"] and "csv" not in sections:
        csv_match = re.search(r'(?:CSV OUTPUT|CSV\s+Output).*?\n(.*?)(?:⸻|\-{3,}|$)', content, re.DOTALL | re.IGNORECASE)
        if csv_match:
            sections["csv"] = csv_match.group(1).strip()
    
    if format_info["has_json_section"] and "json" not in sections:
        json_match = re.search(r'(?:JSON OUTPUT|JSON\s+Output).*?\n(.*?)(?:⸻|\-{3,}|$)', content, re.DOTALL | re.IGNORECASE)
        if json_match:
            sections["json"] = json_match.group(1).strip()
    
    if format_info["has_report_section"] and "report" not in sections:
        report_match = re.search(r'(?:TEXTUAL REPORT|Report).*?\n(.*?)(?:⸻|\-{3,}|$)', content, re.DOTALL | re.IGNORECASE)
        if report_match:
            sections["report"] = report_match.group(1).strip()
    
    # Last resort - direct pattern matching for specific content
    if "csv" not in sections:
        csv_pattern = r'Prediction,Company,Industry,Source,Context,Timeline,Confidence,Stance'
        if re.search(csv_pattern, content):
            # Find the paragraph containing the CSV pattern
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if re.search(csv_pattern, para):
                    sections["csv"] = para.strip()
                    break
    
    if "json" not in sections:
        json_pattern = r'{\s*"nodes"\s*:\s*\['
        if re.search(json_pattern, content, re.DOTALL):
            # Extract the JSON object
            json_match = re.search(r'({[\s\S]*"nodes"[\s\S]*"relationships"[\s\S]*})', content)
            if json_match:
                sections["json"] = json_match.group(1).strip()
    
    if "report" not in sections:
        report_patterns = [
            r'\([A-Z]\).*?Summary of the Prediction',
            r'Summary of the Prediction.*?Market and Strategic Implications'
        ]
        for pattern in report_patterns:
            if re.search(pattern, content, re.DOTALL):
                # Find the section starting with (A), (B), etc.
                report_match = re.search(r'(\([A-Z]\).*?(?:$|⸻))', content, re.DOTALL)
                if report_match:
                    sections["report"] = report_match.group(1).strip()
                    break
    
    # Very last resort - if there are no clear sections, process entire content
    if not sections:
        # Determine the most likely format based on content
        if '{' in content and '}' in content and ('"nodes"' in content or '"relationships"' in content):
            sections["json"] = content
        elif 'Prediction' in content and 'Company' in content and 'Industry' in content:
            sections["csv"] = content
        else:
            sections["report"] = content
    
    return sections

def process_file(input_file):
    """
    Process the input file and generate output files for each format.
    
    Args:
        input_file (str): Path to the input file to process
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Detect the format of the input
        format_info = detect_input_format(content)
        print(f"Detected formats: {format_info['sections']}")
        
        # Extract sections based on format
        sections = extract_sections(content, format_info)
        print(f"Extracted sections: {list(sections.keys())}")
        
        # Get current year for filenames
        current_year = datetime.now().year
        
        # Process each section and save to appropriate file
        if "csv" in sections:
            csv_output = f"BRK_Predictions_{current_year}.csv"
            result = extract_csv_data(sections["csv"], csv_output)
            if result:
                print(f"CSV file generated: {csv_output}")
            else:
                print(f"Error generating CSV file. Section content length: {len(sections['csv'])}")
        else:
            print("No CSV section found to process")
        
        if "json" in sections:
            json_output = f"BRK_Relatons_{current_year}.json"  # Note: keeping the typo as in the requirements
            result = extract_json_data(sections["json"], json_output)
            if result:
                print(f"JSON file generated: {json_output}")
            else:
                print(f"Error generating JSON file. Section content length: {len(sections['json'])}")
        else:
            print("No JSON section found to process")
        
        if "report" in sections:
            pdf_output = f"BRK_Report_{current_year}.pdf"
            result = generate_report(sections["report"], pdf_output)
            if result:
                print(f"PDF report generated: {pdf_output}")
            else:
                print(f"Error generating PDF report. Section content length: {len(sections['report'])}")
        else:
            print("No report section found to process")
            
        if not sections:
            print("Error: Could not identify any sections to process.")
            return False
            
        return True
            
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python brk_extraction_controller.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Check file size
    file_size = os.path.getsize(input_file)
    print(f"Processing file '{input_file}' ({file_size} bytes)")
    
    if file_size == 0:
        print("Error: File is empty.")
        sys.exit(1)
    
    # Process the file
    try:
        success = process_file(input_file)
        if success:
            print("\nAll files have been processed successfully.")
            current_year = datetime.now().year
            print(f"\nOutput files:")
            print(f"- BRK_Predictions_{current_year}.csv")
            print(f"- BRK_Relatons_{current_year}.json")
            print(f"- BRK_Report_{current_year}.pdf")
        else:
            print("\nProcessing completed with errors.")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
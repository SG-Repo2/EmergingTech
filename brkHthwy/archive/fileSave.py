import os
import re
import json
import csv
from datetime import datetime
from fpdf import FPDF

def extract_sections(file_path):
    """
    Extract the three sections from the input file.
    Returns tuple of (csv_content, json_content, report_content)
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into sections using the section markers
    sections = re.split(r'⸻\s*\d+\.\s+', content)
    
    # Clean up section titles and empty sections
    sections = [section.strip() for section in sections if section.strip()]
    
    # Extract content from each section
    csv_section = re.search(r'CSV OUTPUT\s+(.*?)(?=⸻)', content, re.DOTALL).group(1).strip()
    json_section = re.search(r'JSON OUTPUT.*?\s+(.*?)(?=⸻)', content, re.DOTALL).group(1).strip()
    report_section = re.search(r'TEXTUAL REPORT.*?\s+(.*)', content, re.DOTALL).group(1).strip()
    
    return csv_section, json_section, report_section

def save_csv_file(content, output_path):
    """Save CSV content to a file"""
    # Extract the CSV data (skip commentary line)
    csv_lines = [line for line in content.split('\n') if line.strip() and not line.startswith('Below')]
    
    # Write to CSV file
    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for line in csv_lines:
            # Skip empty lines
            if not line.strip():
                continue
            # Handle the header line
            if line.startswith('Prediction'):
                writer.writerow(line.split(','))
            else:
                # For data rows, need to handle commas inside quoted fields
                row = []
                in_quotes = False
                current_field = ""
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                        current_field += char
                    elif char == ',' and not in_quotes:
                        row.append(current_field.strip())
                        current_field = ""
                    else:
                        current_field += char
                        
                # Add the last field
                if current_field:
                    row.append(current_field.strip())
                    
                writer.writerow(row)
    
    print(f"CSV file saved to {output_path}")

def save_json_file(content, output_path):
    """Save JSON content to a file"""
    # Find the JSON object in the content (between brackets)
    json_match = re.search(r'({.*})', content, re.DOTALL)
    if json_match:
        json_text = json_match.group(1)
        
        # Parse and then write to ensure valid JSON
        try:
            json_data = json.loads(json_text)
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=2)
            print(f"JSON file saved to {output_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    else:
        print("No valid JSON found in the content.")

def save_pdf_file(content, output_path):
    """Save the textual report to a PDF file with proper Unicode support using fpdf2."""
    try:
        from fpdf import FPDF  # This will use fpdf2 if installed
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', '', 11)
        
        # Split content into lines and add to PDF
        lines = content.split('\n')
        for line in lines:
            if line.startswith('⸻'):
                pdf.ln(5)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
            elif line.strip().startswith('(') and len(line.strip()) <= 3:
                # Section headers
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 10, line, 0, 1)
                pdf.set_font('Helvetica', '', 11)
            else:
                pdf.multi_cell(0, 5, line)
                pdf.ln(2)
        
        pdf.output(output_path)
        print(f"PDF report saved to {output_path}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        # Fallback to text file
        with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved report as text file instead: {output_path.replace('.pdf', '.txt')}")

def main():
    input_file = "paste.txt"
    
    # Get current year for filenames
    current_year = datetime.now().year
    
    # Define output file paths
    csv_output = f"BRK_Predictions_{current_year}.csv"
    json_output = f"BRK_Relatons_{current_year}.json"  # Note: keeping the typo as requested
    pdf_output = f"BRK_Report_{current_year}.pdf"
    
    # Extract sections from input file
    csv_content, json_content, report_content = extract_sections(input_file)
    
    # Save to output files
    save_csv_file(csv_content, csv_output)
    save_json_file(json_content, json_output)
    save_pdf_file(report_content, pdf_output)
    
    print("All files have been extracted and saved successfully.")

if __name__ == "__main__":
    main()
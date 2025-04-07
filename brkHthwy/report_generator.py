#!/usr/bin/env python3
"""
Financial Prediction Report Generator

This module handles the generation of PDF reports from textual analysis of
forward-looking statements in financial documents. It processes structured
text content and creates a properly formatted PDF report.

The report organizes predictions with sections for:
- Summary of the Prediction
- Context and Rationale
- Market and Strategic Implications
- Risks, Contingencies, and Mitigations
- Confidence and Timeline
"""

import re
from datetime import datetime
from fpdf import FPDF

def generate_report(report_content, output_path):
    """
    Generate a PDF report from textual content.
    
    Args:
        report_content (str): Raw textual report content
        output_path (str): Path where the PDF file will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create PDF document
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts and title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Financial Prediction Analysis Report", ln=True, align='C')
        pdf.ln(5)
        
        # Add the date
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(5)
        
        # Extract and process sections
        sections = extract_report_sections(report_content)
        
        if not sections:
            # If no sections could be extracted, create a single section with all content
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, "Analysis of Forward-Looking Statements\n\n" + report_content.strip())
        else:
            # Add content to PDF
            for section_id, section_content in sections.items():
                add_section_to_pdf(pdf, section_id, section_content)
        
        # Save the PDF
        pdf.output(output_path)
        print(f"Successfully generated PDF report: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_report_sections(report_content):
    """
    Extract the individual prediction sections from the report content.
    
    Args:
        report_content (str): Raw report content
        
    Returns:
        dict: Dictionary of section_id -> section_content
    """
    sections = {}
    print(f"Processing report content ({len(report_content)} chars)")
    
    # First try: Look for labeled sections with the pattern "(A)", "(B)", etc.
    labeled_pattern = r'\(?([A-Z])\)?[\s\n]*([^(]+?)(?=\(?[A-Z]\)?|$|\n\s*\n|⸻)'
    labeled_matches = re.finditer(labeled_pattern, report_content, re.DOTALL)
    for match in labeled_matches:
        section_id = match.group(1)
        section_content = match.group(2).strip()
        if section_content:
            sections[section_id] = section_content
    
    # Second try: Look for sections with explicit dividers
    if not sections:
        print("No labeled sections found, trying divider approach")
        divider_pattern = r'(⸻|\-{3,})'
        divider_sections = re.split(divider_pattern, report_content)
        if len(divider_sections) > 1:
            for i, section in enumerate(divider_sections):
                if section.strip() and not re.match(divider_pattern, section):
                    # Extract a letter identifier if present, otherwise use index
                    letter_match = re.search(r'\(([A-Z])\)', section)
                    if letter_match:
                        section_id = letter_match.group(1)
                    else:
                        section_id = chr(65 + i % 26)  # A, B, C, ...
                    sections[section_id] = section.strip()
    
    # Third try: Look for sections with headers like "Summary of the Prediction"
    if not sections:
        print("No divider sections found, trying header approach")
        patterns = [
            r'(.*?Summary of the Prediction.*?)(?=\n\s*\n|\Z)', 
            r'(.*?Market and Strategic Implications.*?)(?=\n\s*\n|\Z)',
            r'(.*?Risks and Contingencies.*?)(?=\n\s*\n|\Z)',
            r'(.*?Confidence and Timeline.*?)(?=\n\s*\n|\Z)'
        ]
        
        section_counter = 0
        for pattern in patterns:
            matches = re.finditer(pattern, report_content, re.DOTALL)
            for match in matches:
                section_content = match.group(1).strip()
                if section_content:
                    section_id = chr(65 + section_counter)  # A, B, C, ...
                    sections[section_id] = section_content
                    section_counter += 1
    
    # Fourth try: Split by numbered sections (1., 2., etc.)
    if not sections:
        print("No header sections found, trying numbered sections")
        numbered_pattern = r'\n\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.\s+|\Z)'
        numbered_matches = re.finditer(numbered_pattern, report_content, re.DOTALL)
        for match in numbered_matches:
            section_id = match.group(1)
            section_content = match.group(2).strip()
            if section_content:
                sections[section_id] = section_content
    
    # Final fallback: Split by paragraphs
    if not sections:
        print("No structured sections found, using paragraph-based approach")
        paragraphs = re.split(r'\n\s*\n', report_content)
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                section_id = chr(65 + i % 26)  # A, B, C, ...
                sections[section_id] = paragraph.strip()
    
    print(f"Extracted {len(sections)} report sections")
    return sections

def add_section_to_pdf(pdf, section_id, section_content):
    """
    Add a section to the PDF document with proper formatting.
    
    Args:
        pdf (FPDF): The PDF document object
        section_id (str): The section identifier
        section_content (str): The section content
    """
    try:
        # Extract title from first line
        lines = section_content.split('\n')
        title = lines[0].strip()
        
        # If title is too long, truncate it
        if len(title) > 80:
            title = title[:77] + "..."
        
        # Add section header
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"({section_id}) {title}", ln=True)
        pdf.ln(2)
        
        # Process bullet points and subsections
        pdf.set_font("Arial", "", 12)
        current_subsection = ""
        in_bullet_list = False
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue
            
            # Check for bullet points or subsection headings
            if line.startswith('•'):
                # Format as bullet point
                parts = line.split('\t', 1)
                if len(parts) > 1:
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, parts[0], ln=True)
                    
                    pdf.set_font("Arial", "", 12)
                    pdf.multi_cell(0, 10, parts[1])
                else:
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(10, 10, "•", ln=0)
                    pdf.multi_cell(0, 10, line[1:].strip())
                
                in_bullet_list = True
                
            elif line.startswith('-'):
                # Alternative bullet style
                pdf.set_font("Arial", "", 12)
                pdf.cell(10, 10, "-", ln=0)
                pdf.multi_cell(0, 10, line[1:].strip())
                
                in_bullet_list = True
                
            elif re.match(r'^\d+\.\s+', line) or re.match(r'^[a-z]\)\s+', line):
                # Numbered list or sub-bullet
                pdf.set_font("Arial", "", 12)
                match = re.match(r'(^\d+\.\s+|^[a-z]\)\s+)(.*)', line)
                if match:
                    pdf.cell(15, 10, match.group(1), ln=0)
                    pdf.multi_cell(0, 10, match.group(2))
                else:
                    pdf.multi_cell(0, 10, line)
                
                in_bullet_list = True
                
            elif line.endswith(':') or any(keyword in line.lower() for keyword in ['summary', 'context', 'implications', 'risks', 'confidence']):
                # This is likely a subsection header
                pdf.ln(2)
                pdf.set_font("Arial", "B", 12)
                pdf.multi_cell(0, 10, line)
                pdf.set_font("Arial", "", 12)
                pdf.ln(2)
                
                current_subsection = line
                in_bullet_list = False
                
            else:
                # Regular paragraph text
                if in_bullet_list:
                    pdf.ln(2)  # Add spacing after bullet lists
                    in_bullet_list = False
                    
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, line)
        
        pdf.ln(5)  # Add space after each section
    except Exception as e:
        print(f"Error adding section {section_id} to PDF: {e}")
        # Add a simple error note instead
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"({section_id}) Error processing section", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, "This section could not be properly formatted.")
        pdf.ln(5)

# System prompt for report generation
REPORT_SYSTEM_PROMPT = """
You are an expert financial analyst specializing in forward-looking statements and business implications.
Your task is to produce in-depth, business-focused analyses of predictions extracted from financial documents.

For each prediction, structure your analysis with these sections:
1. Summary of the Prediction
   - Brief restatement or paraphrase of the forecast
   - Clarify scope, magnitude, or numeric targets

2. Context and Rationale
   - Why this prediction is made (management commentary, industry conditions, macro factors)
   - Underlying assumptions (market trends, synergies, regulatory changes)

3. Market and Strategic Implications
   - Potential impact on revenue, competition, product strategy, market share
   - How it fits into the company's broader strategy

4. Risks, Contingencies, and Mitigations
   - Elements that could jeopardize outcomes (external/internal)
   - Potential mitigation strategies the company may employ

5. Confidence and Timeline
   - Explanation of certainty level based on language used
   - Expected timeframe and implementation capacity

GUIDELINES:
- Write in a clear, professional business analysis style
- Focus on actionable insights rather than restating facts
- Balance discussion of opportunities and risks
- Support conclusions with evidence from the source material
- Maintain an objective, analytical tone throughout
- Use bullet points for key factors in each section

OUTPUT FORMAT:
A professional business report with clear section headers, concise paragraphs, and actionable insights.
"""

# Action prompt for report generation
REPORT_ACTION_PROMPT = """
Analyze the provided financial text and create a comprehensive business-focused report on the forward-looking statements.

For each prediction, create a detailed section including:
1. Summary of the Prediction - What is being forecasted?
2. Context and Rationale - Why is this prediction being made?
3. Market and Strategic Implications - What impact could this have?
4. Risks, Contingencies, and Mitigations - What could go wrong and how might it be addressed?
5. Confidence and Timeline - How certain is this prediction and when might it occur?

Format each section with clear headers and use bullet points to highlight key factors.
Maintain a professional business analysis tone throughout.
Provide actionable insights rather than just restating the predictions.

Return a professionally structured report that would be valuable to business decision-makers.
"""

if __name__ == "__main__":
    # For testing as standalone module
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        generate_report(content, "test_output.pdf")
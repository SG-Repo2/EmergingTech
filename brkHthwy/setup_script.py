#!/usr/bin/env python3
"""
Setup script for the Berkshire Hathaway Financial Prediction Extraction Framework.
This script creates all necessary files and installs required dependencies.
"""

import os
import sys
import subprocess

def create_file(filename, content):
    """Create a file with the specified content."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filename}")

def install_dependencies():
    """Install required Python dependencies."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fpdf'])
        print("Successfully installed dependencies")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please run: pip install fpdf")

def main():
    """Create all necessary files and set up the environment."""
    print("Setting up Berkshire Hathaway Financial Prediction Extraction Framework...")
    
    # Install dependencies
    install_dependencies()
    
    # Create a README file
    readme_content = """# Berkshire Hathaway Financial Prediction Extraction Framework

This framework processes financial documents to extract forward-looking statements and generate:
1. CSV files with structured prediction data
2. JSON files with Neo4j-ready relationship data
3. PDF reports with business-focused analysis

## Usage

```
python brk_extraction_controller.py <input_file>
```

## Output Files

- `BRK_Predictions_YYYY.csv` - CSV data with prediction details
- `BRK_Relatons_YYYY.json` - JSON data with relationship information
- `BRK_Report_YYYY.pdf` - PDF report with business analysis

## Components

- `brk_extraction_controller.py` - Main controller script
- `csv_extractor.py` - Processes CSV data
- `json_extractor.py` - Processes JSON data
- `report_generator.py` - Generates PDF reports

## Dependencies

- Python 3.6+
- fpdf library
"""
    create_file("README.md", readme_content)
    
    # Create a sample prompt file
    csv_prompt = f"""SYSTEM PROMPT:
{open('csv_extractor.py', 'r').read().split('CSV_SYSTEM_PROMPT = """')[1].split('"""')[0].strip()}

ACTION PROMPT:
{open('csv_extractor.py', 'r').read().split('CSV_ACTION_PROMPT = """')[1].split('"""')[0].strip()}
"""

    json_prompt = f"""SYSTEM PROMPT:
{open('json_extractor.py', 'r').read().split('JSON_SYSTEM_PROMPT = """')[1].split('"""')[0].strip()}

ACTION PROMPT:
{open('json_extractor.py', 'r').read().split('JSON_ACTION_PROMPT = """')[1].split('"""')[0].strip()}
"""

    report_prompt = f"""SYSTEM PROMPT:
{open('report_generator.py', 'r').read().split('REPORT_SYSTEM_PROMPT = """')[1].split('"""')[0].strip()}

ACTION PROMPT:
{open('report_generator.py', 'r').read().split('REPORT_ACTION_PROMPT = """')[1].split('"""')[0].strip()}
"""

    create_file("prompts_csv.txt", csv_prompt)
    create_file("prompts_json.txt", json_prompt)
    create_file("prompts_report.txt", report_prompt)
    
    print("\nSetup complete! You can now run:")
    print("python brk_extraction_controller.py <your_input_file>")

if __name__ == "__main__":
    main()
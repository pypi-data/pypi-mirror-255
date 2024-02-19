#!/usr/bin/env python3

import nbformat
import re
import json
import argparse


# Function to extract and convert to JSON
def extract_and_convert_to_json(file_path):
    # Load the Jupyter notebook
    notebook = nbformat.read(file_path, as_version=4)

    # Extract text from all cells
    extracted_text = []
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            extracted_text.append(cell.source)
        elif cell.cell_type == 'markdown':
            extracted_text.append(cell.source)
    extracted_text_joined = "\n".join(extracted_text)

    # Regular expressions for searching with robustness to spaces
    # works for both single and double quotes
    patterns = {
    "FIRST_NAME": r"first_name\s*=\s*[\'\"](.+?)[\'\"]",
    "LAST_NAME": r"last_name\s*=\s*[\'\"](.+?)[\'\"]",
    "DREXEL_ID": r"drexel_id\s*=\s*[\'\"](.+?)[\'\"]",
    "DREXEL_EMAIL": r"drexel_email\s*=\s*[\'\"](.+?)[\'\"]"
    }


    # Search and extract
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, extracted_text_joined)
        if match:
            # Stripping extra spaces from the extracted value
            extracted_data[key] = match.group(1).strip()

    # Convert to JSON
    return extracted_data

def main():
    parser = argparse.ArgumentParser(description='Extract info from a Jupyter notebook.')
    parser.add_argument('notebook', help='Path to the .ipynb file')
    args = parser.parse_args()

    info = extract_and_convert_to_json(args.notebook)

    if info is not None:
        with open('info.json', 'w') as json_file:
            print("Writing to info.json")
            json.dump(info, json_file)
    else:
        raise ValueError('Required information is missing in the notebook.')

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import nbformat
import os
import argparse

def process_notebook(file_path):
   with open(file_path, 'r', encoding='utf-8') as f:
      nb = nbformat.read(f, as_version=4)

   for cell in nb.cells:
      if cell.cell_type == 'code':
         if 'tags' not in cell.metadata:
               cell.metadata['tags'] = []
         if 'skip-execution' not in cell.metadata['tags']:
               cell.metadata['tags'].append('skip-execution')
      
      if cell.cell_type == 'markdown':
            cell.metadata['editable'] = False

   with open(file_path, 'w', encoding='utf-8') as f:
      nbformat.write(nb, f)

def main():
   parser = argparse.ArgumentParser(description="Process Jupyter notebooks to modify certain cells")
   parser.add_argument('notebook', type=str, help='Jupyter notebook')
   args = parser.parse_args()

   process_notebook(args.notebook)

   print("Processing complete.")

if __name__ == "__main__":
   main()

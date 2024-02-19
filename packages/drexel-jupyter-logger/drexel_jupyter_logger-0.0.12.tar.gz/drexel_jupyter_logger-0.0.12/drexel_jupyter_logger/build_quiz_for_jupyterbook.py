#!/usr/bin/env python3

import nbformat
import os
import argparse

def process_notebook(file_path):
   with open(file_path, 'r', encoding='utf-8') as f:
      nb = nbformat.read(f, as_version=4)

   new_cells = []
   otter_imported = False

   for cell in nb.cells:
      if cell.cell_type == 'code':
         if 'grader.check' not in cell.source and 'import otter' not in cell.source:
               new_cells.append(cell)
      else:
         new_cells.append(cell)

   nb.cells = new_cells

   with open(file_path, 'w', encoding='utf-8') as f:
      nbformat.write(nb, f)

def main():
   parser = argparse.ArgumentParser(description="Process Jupyter notebooks to delete certain cells and add imports")
   parser.add_argument('notebook_dir', type=str, help='Directory containing Jupyter notebooks')
   args = parser.parse_args()

   # Loop through each Jupyter notebook in the directory
   for filename in os.listdir(args.notebook_dir):
      if filename.endswith('.ipynb'):
         process_notebook(os.path.join(args.notebook_dir, filename))

   print("Processing complete.")

if __name__ == "__main__":
   main()

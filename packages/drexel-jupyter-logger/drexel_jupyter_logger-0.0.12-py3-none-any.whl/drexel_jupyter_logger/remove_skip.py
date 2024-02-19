#!/usr/bin/env python3

import nbformat
import sys
import argparse

def process_notebook(notebook_path):
   # Load the Jupyter Notebook
   notebook = nbformat.read(notebook_path, as_version=4)

   # Check and remove "skip execution" tags from each cell
   for cell in notebook.cells:
      if 'metadata' in cell and 'tags' in cell.metadata:
         if 'skip-execution' in cell.metadata.tags:
               if "from friendly.jupyter import *" in cell.source:
                  pass
               else:
                  cell.metadata.tags.remove('skip-execution')

   # Save the modified notebook
   nbformat.write(notebook, notebook_path)
   return notebook_path

def main():
   parser = argparse.ArgumentParser(description="Process Jupyter notebooks to modify certain cells")
   parser.add_argument('notebook', type=str, help='Jupyter notebook')
   args = parser.parse_args()
   process_notebook(args.notebook)

if __name__ == "__main__":
   main()

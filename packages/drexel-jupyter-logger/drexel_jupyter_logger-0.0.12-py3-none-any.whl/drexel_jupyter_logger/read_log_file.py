#!/usr/bin/env python3

import drexel_jupyter_logger
from collections import defaultdict
import json
import argparse
from datetime import datetime

def main(file_name, key=None):
   
   if key == None:
      key = "7mPZKa3gJZn4ng0WJ5TsUmuQC2RK9XBAwTzrTEjbyB0="

   data = drexel_jupyter_logger.decode_log_file(file_name, key=key)
   
   # Parsing the data to find the last entries for required fields
   # This gets the student name
   last_entries = {}
   for entry in data:
      parts = entry.split(", ")
      if parts[0] == 'info' and len(parts) == 4:
         field_name = parts[1]
         field_value = parts[2]
         last_entries[field_name] = field_value
   
   # Extracting timestamps and converting them to datetime objects
   timestamps = [datetime.strptime(row.split(", ")[-1].strip("."), '%Y-%m-%d %H:%M:%S') for row in data]

   # Getting the earliest and latest times
   last_entries["start_time"] = min(timestamps).strftime('%Y-%m-%d %H:%M:%S')
   last_entries["end_time"] = max(timestamps).strftime('%Y-%m-%d %H:%M:%S')

   # This gets the student information dictionary
   student_information = {key.upper(): value for key, value in last_entries.items()}
   
   # Write the dictionary to 'results.json'
   with open('info.json', 'w') as file:
      print("Writing to info.json")
      json.dump(student_information, file)

   
   # Gets the unique question IDs
   q_entries = [entry for entry in data if entry.startswith('q')]

   # Parse the data
   parsed_data = [line.split(', ') for line in q_entries]

   unique_question_IDs = set(row[0] for row in parsed_data)
   
   # Initialize a dictionary to hold the maximum score for each unique value
   max_scores = {unique_value: 0 for unique_value in unique_question_IDs}
   max_possible_score = {unique_value: 0 for unique_value in unique_question_IDs}

   # Loop through each row in the data
   for row in parsed_data:
      unique_value = row[0]
      score = int(row[2])
      possible_score = int(row[3])
      # Update the score if it's higher than the current maximum
      if score > max_scores[unique_value]:
         max_scores[unique_value] = score
      max_possible_score[unique_value] = possible_score
         
   # Initialize a dictionary to hold the sum of scores for each question
   question_scores = defaultdict(int)
   question_max_scores = defaultdict(int)

   # Loop through the max_scores dictionary and sum scores for each question
   for unique_value, score in max_scores.items():
      # Extract question number (assuming it's the number immediately after 'q')
      question_number = int(unique_value.split('_')[0][1:])
      question_scores[question_number] += score
      question_max_scores[question_number] += max_possible_score[unique_value]
      
   # Sorting the dictionary by keys
   question_max_scores = {key: question_max_scores[key] for key in sorted(question_max_scores)}

   # Sorting the dictionary by keys
   question_scores = {key: question_scores[key] for key in sorted(question_scores)}
   
   # Creating the dictionary structure
   result_structure = {
      "tests": []
   }

   # Adding entries for each question
   for question_number in question_scores.keys():
      question_entry = {
         "name": f"Question {question_number}",
         "score": question_scores[question_number],
         "max_score": question_max_scores[question_number],
         "visibility": "visible",
         "output": ""
      }
      result_structure["tests"].append(question_entry)

   # Write the dictionary to 'results.json'
   with open('results.json', 'w') as file:
      print("Writing to results.json")
      json.dump(result_structure, file, indent=4)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Extracts information from log file.')
   parser.add_argument('logfile', help='Path to the .log file')
   args = parser.parse_args()
   
   main(args.logfile)
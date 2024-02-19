#!/usr/bin/env python3

import os
import sys
import re
from datetime import datetime, timezone, timedelta

import json
import argparse

def assignment_JSON(file_path):

        # Extracting questions to a list of dictionaries, including parsing the 'output' field
        with open(file_path, 'r') as file:
                full_data = json.load(file)

        # Extracting questions to a list of dictionaries, including parsing the 'output' field
        extracted_questions = []

        for number, questions in enumerate(full_data['tests']):
                
                visibility_value = questions.get('visibility', '')
                is_visible = True if visibility_value == "visible" else False
                
                questions_dict = {
                "question_id": number + 1,
                'questions_name': questions.get('name', ''),
                'visibility': is_visible,
                'status': questions.get('status', ''),
                'output': questions.get('output', ''),
                'max_score': questions.get('max_score', '0'),
                'score': questions.get('score', '0')
                }
                
                extracted_questions.append(questions_dict)
                
        return extracted_questions

def save_student_score_report(assignment_id, 
                                student_info, 
                                total_score, 
                                max_total_score, 
                                percentage_score, 
                                scores_data, 
                                file_path):
        """
        Generates and saves a student's score report as a markdown file.

        :param assignment_id: The ID of the assignment.
        :param student_info: Dictionary containing student's first_name, last_name, student_id, and email.
        :param total_score: The total score obtained by the student.
        :param max_total_score: The maximum possible score.
        :param percentage_score: The percentage score.
        :param scores_data: List of dictionaries, each containing question_id, score, max_score, and visibility.
        :param file_path: Path where the markdown file will be saved.
        """
        
        # Get the current UTC time
        now_utc = datetime.now(timezone.utc)

        # East Coast of the United States is typically UTC-5, but during Daylight Saving Time it's UTC-4
        # Checking if it's Daylight Saving Time
        east_coast_time = now_utc - timedelta(hours=4 if now_utc.dst() else 5)

        # Format the date and time in a nice string format
        formatted_date_time = east_coast_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Building the markdown content
        markdown_content = f"# Score for {assignment_id}\n\n"
        markdown_content += "### Student Information\n"
        markdown_content += f"- **First Name:** {student_info['first_name']}\n"
        markdown_content += f"- **Last Name:** {student_info['last_name']}\n"
        markdown_content += f"- **Student ID:** {student_info['student_id']}\n"
        markdown_content += f"- **Email:** {student_info['email']}\n"
        markdown_content += f"- **Submission Time:** {formatted_date_time}\n\n"

        markdown_content += "### Scores\n\n"
        markdown_content += "| Total Score | Maximum Score | Percentage |\n"
        markdown_content += "|-------------|---------------|------------|\n"
        markdown_content += f"| {total_score} | {max_total_score} | {percentage_score:0.2f}% |\n\n"

        markdown_content += "### Detailed Scores\n\n"
        markdown_content += "| Question ID | Score | Max Score | Visibility |\n"
        markdown_content += "|-------------|-------|-----------|------------|\n"
        for score in scores_data:
                visibility = "Visible" if score['visible'] else "Hidden"
                markdown_content += f"| {score['question_id']} | {score['score']} | {score['max_score']} | {visibility} |\n"

        # Writing to a markdown file
        with open(file_path, 'w') as file:
                file.write(markdown_content)

        return file_path

def main():
        parser = argparse.ArgumentParser(description='Extract info from otter results file.')
        parser.add_argument('results', help='Path to the results.json file')
        parser.add_argument('student_id', help='Student ID')
        parser.add_argument('first_name', help='first_name')
        parser.add_argument('last_name', help='last_name')
        parser.add_argument('email', help='email')
        parser.add_argument('assignment_id', help='Assignment ID')
        parser.add_argument('base_name', help='Base name for the output file')
        args = parser.parse_args()
        
        # need to parse the extracted json file
        json_extracted = assignment_JSON(args.results)

        # Get the current UTC time
        now_utc = datetime.now(timezone.utc)

        # East Coast of the United States is typically UTC-5, but during Daylight Saving Time it's UTC-4
        # Checking if it's Daylight Saving Time
        east_coast_time = now_utc - timedelta(hours=4 if now_utc.dst() else 5)

        # Format the date and time in a nice string format
        formatted_date_time = east_coast_time.strftime("%Y-%m-%d %H:%M:%S")

        # calculate the total score
        total_score = sum(float(d.get("score", 0)) for d in json_extracted)
        max_score = sum(float(d.get("max_score", 0)) for d in json_extracted)

        percentage_score = (total_score/max_score)*100

        dict = []
                
        for data in json_extracted:

                dict.append({"date_time": f"{formatted_date_time}",
                        "question_id": data.get('question_id'),
                        "score": data.get('score', 0),
                        "max_score": data.get('max_score', 0),
                        "output": data.get('output', 'NA'),
                        "visible": data.get('visibility', True)
                        })
                
        # Sample student information
        student_info = {
        "first_name": f"{args.first_name}",
        "last_name": f"{args.last_name}",
        "student_id": f"{args.student_id}",
        "email": f"{args.email}"
        }

        # Sample assignment information
        assignment_id = f"{args.assignment_id}"

        save_student_score_report(assignment_id, 
                                student_info, 
                                total_score, 
                                max_score, 
                                percentage_score, 
                                dict, 
                                f"{args.base_name}_Grade_Report.md")

if __name__ == "__main__":
        main()

# Test Call
# python extract_score.py /home/ferroelectric/PRIVATE_ENGR131_W24-1/labs/lab_1/dist/test_solution/results.json 12345 John Doe johndoe@example.com Homework_1

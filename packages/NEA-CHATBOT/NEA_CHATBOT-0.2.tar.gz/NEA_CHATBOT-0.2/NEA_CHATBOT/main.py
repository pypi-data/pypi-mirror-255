# chatbot/utils.py
import json
from typing import Dict


def get_response(question: str, data_file: str = 'Explanation.json') -> str:
    with open(data_file, 'r') as file:
        data = json.load(file)
    questions = data.get('questions', {})
    return questions.get(question, 'Unknown question ID')


def get_hint(question: str, data_file: str = 'Hints.json') -> str:
    with open(data_file, 'r') as file:
        data = json.load(file)
    questions = data.get('questions', {})
    return questions.get(question, 'Unknown question ID')


def generate(question_type: str, question_number: str, type_help: int) -> str:
    question_id = f"{question_type}-{question_number}"
    if type_help == 2:
        return "This guide explains how to utilize the chatbot effectively! Find the question-id in the QUIZ TAB, select the question type and number from the dropdown menu. For instance, 'Int-1' means choosing Int and 1 from the dropdown menu. Then, select either Hint or Explanation for assistance."
    elif type_help == 1:
        return get_response(question_id)
    elif type_help == 0:
        return get_hint(question_id)


def insert_message(msg: str, sender: str, text_widget=None):
    if not msg:
        return
    msg = f"{sender}: {msg}\n\n"
    if text_widget:
        text_widget.configure(state="normal")
        text_widget.insert("end", msg)
        text_widget.configure(state="disabled")
        text_widget.see("end")
    else:
        print(msg)


# app.py

from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re


load_dotenv()

app = Flask(__name__)
app.secret_key="AIzaSyDZEMVP"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    print("startedddd.....")
    return render_template('index.html')


@app.route('/get_details', methods=['POST'])
def get_details():
    if request.method == 'POST':
        pdf_file = request.files['resume']
        file_path = os.path.join('uploads', pdf_file.filename)
        pdf_file.save(file_path)
        if file_path:
            resume_text1 = extract_text_from_pdf(file_path)
            res = model.generate_content(["Generate summary for the given text in structured format containg headings,side headings with its respective html tags example <h1>Heading1</h></p><matter for heading1</p>", resume_text1])
            session['resume_text'] = res.text
            return render_template("resume_details.html",details = res.text)
        else:
             return render_template("resume_details.html",details="")


@app.route('/conduct_interview', methods=['POST'])
def conduct_interview():
            resume_text = session.get('resume_text')
            questions = generate_interview_questions(resume_text)
            return render_template("interview.html",questions=questions)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    if request.method == 'POST':
        # Process the submitted answers
        answers_data = request.form.get('answersData')
        res = model.generate_content(["This is conversation between an interviewer and an interviewee, inform him how performed in this interview by giving some score out of 5, generate it in a way by adding h3 tags to evaluation metrics and h2 tags to scores"])
        return render_template("score.html",answers_data=answers_data,ress = res.text)

def extract_text_from_pdf(pdf_file):
    with open(pdf_file, "rb") as f:
        reader = PdfReader(f)
        text1 = ""
        for page in reader.pages:
            text1 += page.extract_text()
    return text1

def generate_interview_questions(resume_text):
    prompt = """Take this resume text and generate 10 interviews questions and technically based details mentioned in the resume in the list format start with wishing the interviewee and length of the question not more than 20words
    example format in LIST FORMAT
    ["Good Morning lets start the interview","can you start by introducing yourself",Tell your hobbies and interests]"""
    chat = model.start_chat(history=[])
    res = chat.send_message([prompt, resume_text])
    sentences = re.split(r'\d+\.', res.text)
    questions = [sentence.strip() for sentence in sentences if sentence.strip()]
    return questions

if __name__ == '__main__':
    app.run(debug=True)

import os
import glob
from flask import Flask, request, jsonify
import logging
from atlassian.jira import Jira
from llms.openai import openaif
from dotenv import load_dotenv

app = Flask(__name__) 
load_dotenv()
api_key=os.environ.get('OPENAI_KEY')
open_ai = openaif(api_key, messages=[{
        "role": "system",
        "content": " You are an expert project manager tasked with meticulously outlining projects for engineers to work on."
    },])

#@app.route("/", defaults={"path": "index.html"})
#@app.route("/<path:path>")
#def static_file(path):
#    path1 = app.instance_path
#    return app.send_static_file(path)


# message / reply format
@app.route("/sendchat", methods=["POST", "GET"])
def chat():
    message = request.json["message"]
    answer = open_ai.user_request(message)
    return {"reply": answer}


# message / reply format
@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    a = Jira()
    issues =  a.searchIssuesByProjectName('MyHero')
    answer = ask_ai(issues)
    print(answer)
    return {"reply": answer}


def ask_ai(tasks):
    prompt = """
        I am developing mobile application for generating stories with images. 
        I have two version of application in parallel, one for android and one for iOS
        Following are the tasks I have, some of which I have finished.\n
    """
    prompt += str(tasks)
    prompt += """
        Please give us suggestion on tasks I have created but not finished.
        Are they contradictory or duplicate to any previous tasks we have? If so, please give us the title
        of the task and the reason why it is contradictory or duplicate.
        Also, is there task or subtask I am missing? If so, please tell me the summary of one new task I should have made. \nYour entire response should be in HTML format, and under no circumstances should your response contain function definitions.. "
    """
    print(len(open_ai.messages))
    return open_ai.user_request(prompt)


from flask import g
from flask import session
import os
from story.utils import *
import json
from flask import Flask, render_template, request, abort
from story.story_manager import *
from generator.web.web_generator import *
from other.cacher import *
import numpy as np

app = Flask(__name__)
app.secret_key = '#d\xe0\xd1\xfb\xee\xa4\xbb\xd0\xf0/e)\xb5g\xdd<`\xc7\xa5\xb0-\xb8d0S'
CRED_FILE = "./AI-Adventure-2bb65e3a4e2f.json"
story = Story("")

# Bread and butter of app, updates story and returns based on choice
@app.route('/generate', methods=['POST'])
def generate():
    action = request.form["action"]

    # If there is no story in session, make a new one
    if "prompt" not in session or session["prompt"] is None:
        session["prompt"] = get_story_start("classic")
        response = "Continue the initial story block:\n\n" + session["prompt"]

    # If there is a story in session continue from it.
    elif "story" not in session or session["story"] is None:
        story_start = session["prompt"] + action
        story.story_start = story_start

        session["story"] = story.to_json()
        response = "Enter the action then two newlines then the result:\n\n> "

    else:
        story = story.initialize_from_json(session["story"])
        action, result = action.split("\n")
        story.add_to_story(action, result)
        session["story"] = story.to_json()

        response = "Enter the action then two newlines then the result:\n\n> "

    print("Returning response")
    return response

# Routes to index
@app.route('/')
def root():
    session["story"] = None
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
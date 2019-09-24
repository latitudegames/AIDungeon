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
generator = WebGenerator(CRED_FILE)
story_manager = CachedStoryManager(generator, CRED_FILE)

def get_response_string(story_text, possible_actions):
    string_list = ["\n\n", story_text, "\n\nOptions:" + "\n"]
    for i, action in enumerate(possible_actions):
        string_list.append(str(i) + ") " + action + "\n")
    string_list.append("\nWhich action do you choose? ")

    response = "".join(string_list)
    return response

# Shows about. (Should also link to paper when published)
@app.route('/about.html')
def about():
    return render_template('about.html')

# Bread and butter of app, updates story and returns based on choice
@app.route('/generate', methods=['POST'])
def generate():
    action = request.form["action"]

    # If there is no story in session, make a new one
    if "story" not in session or session["story"] is None:
        print("Starting new story")
        seed = np.random.randint(100)
        prompt = get_story_start("classic")
        story_manager.start_new_story(prompt, seed)
        possible_actions = story_manager.get_possible_actions()
        response = get_response_string(str(story_manager.story), possible_actions)

    # If there is a story in session continue from it.
    else:
        print("Using existing story")
        story = session["story"]
        story_manager.load_story(story, from_json=True)

        result, possible_actions = story_manager.act(action)
        if result is None:
            response = "\nInvalid choice. Must be a number from 0 to 3. \n" + "\nWhich action do you choose? "
        else:
            response = get_response_string(result, possible_actions)

    session["story"] = story_manager.json_story()
    print("Returning response")
    return response

# Routes to index
@app.route('/')
def root():
    session["story"] = None
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
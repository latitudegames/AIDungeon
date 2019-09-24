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


# Initializes everything for a session
def story_init(session, seed):
    session["generator"] = WebGenerator(CRED_FILE)
    session["seed"] = seed
    session["story_manager"] = CachedStoryManager(generator, 0, session["seed"], CRED_FILE)

# Shows about. (Should also link to paper when published)
@app.route('/about.html')
def about():
    return render_template('about.html')

# Bread and butter of app, updates story and returns based on choice
@app.route('/generate', methods=['POST'])
def generate():
    print("Entered generate")

    if "story_manager" not in session:
        print("not initialized")
        seed = np.random.randint(100)
        story_init(session, seed)
        story_manager = session["story_manager"]
        possible_actions = story_manager.get_possible_actions()
        string_list = [str(story_manager.story), "\n\nOptions:" + "\n"]
        for i, action in enumerate(possible_actions):
            string_list.append(str(i) + ") " + action)

        response = "".join(string_list)

    else:
        print("initialized")
        story_manager = session["story_manager"]
        action = request.form["action"]
        result, possible_actions = story_manager.act(action_choice)
        if result is None:
            response = "Invalid choice. Must be a number from 0 to 3. \n"
        else:
            string_list = [response]
            for i, action in enumerate(possible_actions):
                string_list.append(str(i) + ") " + action)
            response = "".join(string_list)

    return response

# Routes to index
@app.route('/')
def root():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
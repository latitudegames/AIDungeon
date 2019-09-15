from flask import g
from flask import session
import os
from story.utils import *
import json
from flask import Flask, render_template, request, abort
from story.story_manager import *
from generator.web.web_generator import *
from other.caching import *

app = Flask(__name__)
app.secret_key = '#d\xe0\xd1\xfb\xee\xa4\xbb\xd0\xf0/e)\xb5g\xdd<`\xc7\xa5\xb0-\xb8d0S'
GOOGLE_CRED_LOCATION = "./AI-Adventure-2bb65e3a4e2f.json"

@app.route('/')
def root():
    seed = -1
    data = {'seed': seed}
    return render_template('index.html', data=data)


@app.route('/<seed>')
def rootseed(seed):
    if seed == "":
        seed = -1
    else:
        seed = int(seed)
    data = {'seed': seed}
    session["seed"] = seed
    return render_template('index.html', data=data)


@app.route('/index.html')
def index():
    data = {'seed': -1}

    return render_template('index.html', data=data)


@app.route('/about.html')
def about():
    return render_template('about.html')



# generator = WebGenerator("./AI-Adventure-2bb65e3a4e2f.json")
#     prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
#     story_manager = ConstrainedStoryManager(generator, prompt)
#
#     console_print(str(story_manager.story))
#     possible_actions = story_manager.get_possible_actions()
#     while (True):
#         console_print("\nOptions:")
#         for i, action in enumerate(possible_actions):
#             console_print(str(i) + ") " + action)
#
#         result = None
#         while(result == None):
#             action_choice = input("Which action do you choose? ")
#             print("\n")
#             result, possible_actions = story_manager.act(action_choice)
#
#         console_print(result)


def story_init(session, seed):
    session["seed"] = seed
    prompt_num = 0
    session["prompt_num"] = prompt_num
    session["generator"] = WebGenerator(GOOGLE_CRED_LOCATION)

    first_story = retrieve_from_cache(seed, prompt_num, [], "story")


    if prompt is None:

        prompt = prompts[prompt_num]
        response = generate_story_block(prompt, local=RUN_LOCAL)
        cache_file(seed, prompt_num, [], response, "story")

    session["story_manager"] = ConstrainedStoryManager(session["generator"], prompt)
    session["initialized"] = True


@app.route('/generate', methods=['POST'])
def story_request():
    print("****Generating Story****")
    seed = request.form["seed"]
    prompt_num = int(request.form["prompt_num"])
    gen_actions = request.form["actions"]

    if "initialized" not in session:
        story_init(session, seed, prompt_num)

    print("Session Seed is ", session["seed"])

    if int(seed) < 0 or int(seed) > 100:
        abort(404)

    if gen_actions == "true":

        #prompt = request.form["prompt"]
        choices = json.loads(request.form["choices"])
        #print("Getting response for seed ", seed, " prompt_num ", prompt_num, " and choices ", choices)

        action_results = retrieve_from_cache(seed, prompt_num, choices, "choices")

        if action_results is not None:
            response = action_results
        else:
            last_action_result = request.form["last_action_result"]
            prompt = continuing_prompts[prompt_num] + last_action_result
            #print("\n\nAction prompt is \n ", prompt)
            action_results = [generate_action_result(prompt, phrase, local=RUN_LOCAL) for phrase in phrases]
            response = json.dumps(action_results)
            cache_file(seed, prompt_num, choices, response, "choices")
    else:

        result = retrieve_from_cache(seed, prompt_num, [], "story")

        if result is not None:
            response = result
        else:
            prompt = prompts[prompt_num]
            response = generate_story_block(prompt, local=RUN_LOCAL)
            cache_file(seed, prompt_num, [], response, "story")


    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_render_template]
import datetime
from generator import StoryGenerator
import tensorflow as tf
from flask import g
import pdb
import os

#os.environ['GOOGLE_APPLICATION_CREDENTIALS']="/home/nickwalton/git/DM-Server/AI-Adventure-1f64082e4e50.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS']="/home/nickwalton00/DM-Server/AI-Adventure-1f64082e4e50.json"

from google.cloud import storage
from google import cloud
import json
from flask import Flask, render_template, request
storage_client = storage.Client()
bucket = storage_client.get_bucket("dungeon-cache")

app = Flask(__name__)

phrases = [" You attack", " You use", " You tell", " You go"]
prompts = ["You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"]

session = None
generator = None

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    return render_template('index.html')
    
    
def cache_file(seed, prompt_num, choices, response, tag):

    blob_file_name = "p" + str(prompt_num) + "/seed" + str(seed) + "/" + tag
    for action in choices:
        blob_file_name = blob_file_name + str(action)
    blob = bucket.blob(blob_file_name)
    
    blob.upload_from_string(response)
    
    print("File ", blob_file_name, " cached")


def retrieve_from_cache(seed, prompt_num, choices, tag):
    blob_file_name = "p" + str(prompt_num) + "/seed" + str(seed) + "/" + tag
    
    for action in choices:
        blob_file_name = blob_file_name + str(action)
        
    blob = bucket.blob(blob_file_name)
    
    if blob.exists(storage_client):
        result = blob.download_as_string().decode("utf-8")
        print(blob_file_name, " found in cache")
    else:
        result = None
        print(blob_file_name, " not found in cache")
        
    return result
    

@app.route('/generate', methods=['POST'])
def story_request():
    print("****Generating Story****")
    seed = request.form["seed"]
    prompt_num = int(request.form["prompt_num"])
    gen_actions = request.form["actions"] 
   
    
    generator = get_generator()
    
    if gen_actions == "true":

        prompt = request.form["prompt"] 
        choices = json.loads(request.form["choices"]) # used for caching lookup
        print("Getting response for seed ", seed, " prompt_num ", prompt_num, " and choices ", choices)
    

        # TODO implement caching based on seed, prompt_num and choices
        action_results = retrieve_from_cache(seed, prompt_num, choices, "choices")
        
        if action_results is not None:
            response = action_results
        else:
            action_results = [generator.generate_action_result(prompt, phrase) for phrase in phrases]
            response = json.dumps(action_results)
            cache_file(seed, prompt_num, choices, response, "choices")
    else:
        print("Getting response for seed ", seed, " prompt_num ", prompt_num)

        # TODO implement caching based on seed, and prompt_num
        result = retrieve_from_cache(seed, prompt_num, [], "story")
        if result is not None:
            response = result
        else:
            prompt = prompts[prompt_num]
            response = generator.generate_story_block(prompt)
            cache_file(seed, prompt_num, [], response, "story")
        
    print("\nGenerated response is: \n", response)
    print("")
    
    return response
    
    
def get_generator():
    if "gen" not in g:
        if "sess" not in g:
            g.sess = tf.Session()
        g.gen = StoryGenerator(g.sess)
        
    return g.gen
    
@app.teardown_appcontext
def teardown_sess(_):
    sess = g.pop("sess",None)
    
    if sess is not None:
        sess.close()

def generate_cache():
    
    for seed in range(100):
        result = retrieve_from_cache(seed, prompt_num, [], "story")
        if result is not None:
            response = result
        else:
            prompt = prompts[prompt_num]
            response = generator.generate_story_block(prompt)
            cache_file(seed, prompt_num, [], response, "story")
            
            
    action_queue = [[i, 0, []] for i in range(100)]    
    
    while(True):
        
        next_gen = action_queue.pop(0)
        seed = next_gen[0]
        prompt_num = next_gen[1]
        choices = next_gen[2]
        
        action_results = retrieve_from_cache(seed, prompt_num, choices, "choices")
        
        if action_results is not None:
            response = action_results
        else:
            action_results = [generator.generate_action_result(prompt, phrase) for phrase in phrases]
            response = json.dumps(action_results)
            cache_file(seed, prompt_num, choices, response, "choices")
            
        for j in range(4):
            new_choices = choices[:]
            new_choices.append(j)
            action_queue.append([seed, 0, new_choices])


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    #with tf.Session(graph=tf.Graph()) as sess:
    #   app.run(host='127.0.0.1', port=8090, debug=False)
    
    
        
    
    
    
    
    # Run Caching
    
        
        
        
        
# [START gae_python37_render_template]

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
from flask import g
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS']="./AI-Adventure-2bb65e3a4e2f.json"

from google.cloud import storage
from google import cloud
import json
from flask import Flask, render_template, request, abort
storage_client = storage.Client()
bucket = storage_client.get_bucket("dungeon-cache")
from flask import Response
import requests
app = Flask(__name__)
import gpt2.src.encoder as encoder


# App Info
phrases = [" You attack", " You use", " You tell", " You go"]
prompts = ["You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"]
requested_map = {}

encoder_path='gpt2/models/117M'

enc = encoder.get_encoder(encoder_path)

project = "ai-adventure"
model = "generator_v1"
version = "version2"

def predict(context_tokens):
    
    # Create the ML Engine service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)
    instance = json.loads(context_tokens)

    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects(). predict(
        name=name,
        body={'instances': [instance]}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']



def generate(prompt):
    context_tokens = [enc.encode(prompt)]
    
    
    pred = predict(context_tokens)
    
    
    output = enc.decode(pred[0])
    return output




@app.route('/')
def root():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')


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

    if int(seed) < 0 or int(seed) > 1000:
        print("Invalid seed: " + seed)
        abort(404)

    if gen_actions == "true":

        prompt = request.form["prompt"]
        choices = json.loads(request.form["choices"])
        print("Getting response for seed ", seed, " prompt_num ", prompt_num, " and choices ", choices)

        action_results = retrieve_from_cache(seed, prompt_num, choices, "choices")

        if action_results is not None:
            response = action_results
        else:
            response = requests.post(gen_ip + "/generate",
                                     data={"actions":"true","seed":seed, "prompt_num":prompt_num, "prompt": prompt, "choices": json.dumps(choices)})
            response = response.text
            cache_file(seed, prompt_num, choices, response, "choices")
    else:

        print("Getting response for seed ", seed, " prompt_num ", prompt_num)
        result = retrieve_from_cache(seed, prompt_num, [], "story")

        if result is not None:
            response = result
        else:
            response = requests.post(gen_ip + "/generate", data={"actions":"false","seed":seed, "prompt_num":prompt_num})
            response=response.text
            cache_file(seed, prompt_num, [], response, "story")

    print("\nGenerated response is: \n", response)
    print("")

    return response

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)



# [START gae_python37_render_template]

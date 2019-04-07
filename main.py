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

import json
from flask import Flask, render_template, request

app = Flask(__name__)

session = None
generator = None

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    return render_template('index.html')
    
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
    
@app.errorhandler(400)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 400


@app.route('/generate', methods=['POST'])
def story_request():
    print("****Generating Story****")
    prompt = request.form["prompt"] # given prompt
    phrase = request.form["phrase"]
    gen_actions = request.form["actions"] # given prompt
    
    print("\n Given prompt is: \n",prompt,"\n")
    
    generator = get_generator()
    
    if gen_actions == "true":
        action, result = generator.generate_action_result(prompt, phrase)
        response = json.dumps([action, result])
    else:
        response = generator.generate_story_block(prompt)
        
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


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    with tf.Session(graph=tf.Graph()) as sess:
       app.run(host='127.0.0.1', port=8090, debug=False)
        
        
        
        
# [START gae_python37_render_template]

from flask import g
from flask import session
import os
import googleapiclient.discovery
from story.utils import *
from google.cloud import storage
import json
from flask import Flask, render_template, request, abort
from generator import StoryGenerator
import gpt2.src.encoder as encoder

# Model/Cache Info
storage_client = storage.Client()
bucket = storage_client.get_bucket("dungeon-cache")


def cache_file(seed, prompt_num, choices, response, tag):

    blob_file_name = "prompt" + str(prompt_num) + "/seed" + str(seed) + "/" + tag
    for action in choices:
        blob_file_name = blob_file_name + str(action)
    blob = bucket.blob(blob_file_name)

    blob.upload_from_string(response)

    print("File ", blob_file_name, " cached")


def retrieve_from_cache(seed, prompt_num, choices, tag):
    blob_file_name = "prompt" + str(prompt_num) + "/seed" + str(seed) + "/" + tag

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

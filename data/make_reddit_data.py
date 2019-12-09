import json
import os

from story.utils import *


def load_stories(file):

    try:
        with open(file) as fp:
            stories = json.load(fp)
            return stories
    except:
        with open(file) as fp:
            stories = []
            for line in fp:
                if len(line) > 10:
                    story = json.loads(line)
                    stories.append(story)
            return stories


def modify_story(story):

    text = story["body"]
    if len(text) < 100:
        return None

    first_person = is_first_person(text)
    second_person = is_second_person(text)
    if first_person or second_person:
        return first_to_second_person(text)
    else:
        return None


current = os.getcwd()
files = os.listdir(current + "/writingprompts")
output_file_path = "writing_prompts.txt"
with open(output_file_path, "w") as output_file:
    filenames = ["writingprompts/" + file for file in files]
    cleaned_stories = []
    for filename in filenames:
        print("Processing file ", filename)
        stories = load_stories(filename)
        for story in stories:
            cleaned_story = modify_story(story)
            if cleaned_story is not None:
                cleaned_stories.append(cleaned_story)

    raw_text = ""
    start_token = "<|startoftext|>"
    end_token = "<|endoftext|>"
    for story in cleaned_stories:
        raw_text += start_token + story + end_token + "\n"
        print(len(raw_text))

    output_file.write(raw_text)

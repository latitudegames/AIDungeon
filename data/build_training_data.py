import csv
import json
from story.utils import *


def load_tree(filename):
    with open(filename, 'r') as fp:
        tree = json.load(fp)
    return tree

def remove_phrase(text):
    phrases = ["Years pass...", "Years pass"]
    for phrase in phrases:
        text = text.replace(phrase, "")
    return text

def make_stories(current_story, tree):
    stories = []
    action = first_to_second_person(tree["action"])
    action = remove_phrase(action)
    result = remove_phrase(tree["result"])
    current_story += ("\n> " + action + "\n" + result)

    action_results = tree["action_results"]
    if len(action_results) == 0 or action_results[0] is None:
        return [current_story]
    else:
        stories += make_stories(current_story, action_results[0])

        for i in range(1, len(action_results)):
            if action_results[i] is not None:
                stories += make_stories(tree["result"], action_results[i])

    return stories

def get_stories(filename):
    tree = load_tree(filename)
    stories = []
    for action_result in tree["action_results"]:
        stories += make_stories(tree["first_story_block"], action_result)
    return stories


output_file_path = "text_adventures.txt"
with open(output_file_path, 'w') as output_file:
    filenames = ["stories/story" + str(i) + ".json" for i in range(0,41)]
    stories = []
    for filename in filenames:
        stories += get_stories(filename)
        print(len(stories))

    raw_text = ""
    start_token = "<|startoftext|>"
    end_token = "<|endoftext|>"
    for story in stories:
        raw_text += start_token + story + end_token + "\n"
        print(len(raw_text))

    output_file.write(raw_text)




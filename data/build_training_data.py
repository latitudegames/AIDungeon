import csv
import json

from story.utils import *


def load_tree(filename):
    with open(filename, "r") as fp:
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
    action_list = action.split(" ")
    first_word = action_list[0]
    if first_word[-1] == ".":
        first_word = first_word[:-1]

    dont_add_you = [
        "the",
        "another",
        "next",
        "in",
        "monday",
        "back",
        "a",
        "years",
        "one",
        "two",
        "during",
        "months",
        "weeks",
        "seven",
        "three",
        "...",
        "twelve",
        "four",
        "five",
        "six",
        "blackness...",
        "you",
        "no",
        "yes",
        "up",
        "down",
        "onward",
    ]

    if action[0] is '"':
        last_quote = action.rfind('"')
        action = "You say " + action[: last_quote + 1]
    elif first_word.lower() not in dont_add_you:
        action = "You " + action[0].lower() + action[1:]

    action = remove_phrase(action)
    result = remove_phrase(tree["result"])
    current_story += "\n> " + action + "\n" + result

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
with open(output_file_path, "w") as output_file:
    filenames = ["stories/story" + str(i) + ".json" for i in range(0, 93)]
    # filenames = []
    for filename in filenames:
        tree = load_tree(filename)
        print('"' + tree["tree_id"] + '",')

    filenames += ["stories/crowdsourcedstory" + str(i) + ".json" for i in range(0, 12)]
    stories = []
    for filename in filenames:
        filename_stories = get_stories(filename)
        stories += filename_stories
        print(len(stories))

    raw_text = ""
    start_token = "<|startoftext|>"
    end_token = "<|endoftext|>"
    for story in stories:
        raw_text += start_token + story + end_token + "\n"
        print(len(raw_text))

    output_file.write(raw_text)

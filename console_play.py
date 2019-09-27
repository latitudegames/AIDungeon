import os
from story.utils import *
from google.cloud import storage
import json
from story.story_manager import *
from generator.web.web_generator import *
from generator.ctrl.ctrl_generator import *
import tensorflow as tf
import textwrap

CRED_FILE = "./AI-Adventure-2bb65e3a4e2f.json"

# Set the key
def console_print(str, pycharm=False):
    if pycharm:
        LINE_WIDTH=80

        print((textwrap.fill(str, LINE_WIDTH)))
    else:
        print(str)


def play_unconstrained():
    generator = CTRLGenerator()
    #generator = WebGenerator(CRED_FILE)
    prompt = get_story_start("vague_police")
    story_manager = UnconstrainedStoryManager(generator)
    story_manager.start_new_story(prompt)

    print("\n")
    console_print(str(story_manager.story))
    while (True):
        action = ""
        while(action == ""):
            action = input("> ")

        action = " You " + action + ". "
        action = first_to_second_person(action)
        result = story_manager.act(action)
        console_print("\n\n" + action + result)


def play_constrained():
    print("\n")
    generator = WebGenerator(CRED_FILE)
    #generator = CTRLGenerator()
    story_start = "haunted"
    prompt = get_story_start(story_start)
    story_manager = CTRLStoryManager(generator)
    story_manager.start_new_story(prompt)

    console_print("\n")
    console_print(str(story_manager.story))
    possible_actions = story_manager.get_possible_actions()
    while (True):
        console_print("\nOptions:")
        for i, action in enumerate(possible_actions):
            console_print(str(i) + ") " + action)

        result = None
        while(result == None):
            action_choice = input("Which action do you choose? ")
            if action_choice is "print story":
                print(story_manager.story)
                continue
            print("\n")
            result, possible_actions = story_manager.act(action_choice)

        console_print(result)


def play_cached():
    generator = WebGenerator(CRED_FILE)
    story_manager = ConstrainedStoryManager(generator)
    story_manager.enable_caching(CRED_FILE)

    story_manager.start_new_story(get_story_start("classic"), 0)

    console_print(str(story_manager.story))
    possible_actions = story_manager.get_possible_actions()
    while (True):
        console_print("\n\nOptions:")
        for i, action in enumerate(possible_actions):
            console_print(str(i) + ") " + action)

        result = None
        while(result == None):
            action_choice = input("Which action do you choose? ")
            print("\n")
            result, possible_actions = story_manager.act(action_choice)

        console_print(result)

def play_cached_hospital():
    print("\n")
    generator = CTRLGenerator()
    story_start = "haunted"
    prompt = get_story_start(story_start)
    story_manager = CTRLStoryManager(generator)
    story_manager.enable_caching(CRED_FILE, bucket_name="haunted-hospital")

    story_manager.start_new_story(prompt)

    console_print("\n")
    console_print(str(story_manager.story))
    possible_actions = story_manager.get_possible_actions()
    while (True):
        console_print("\nOptions:")
        for i, action in enumerate(possible_actions):
            console_print(str(i) + ") " + action)

        result = None
        while (result == None):
            action_choice = input("Which action do you choose? ")
            if action_choice is "print story":
                print(story_manager.story)
                continue
            print("\n")
            result, possible_actions = story_manager.act(action_choice)

        console_print(result)


if __name__ == '__main__':
    play_unconstrained()




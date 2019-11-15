import os
from story.utils import *
from google.cloud import storage
import json
from story.story_manager import *
# from generator.web.web_generator import *
# from generator.ctrl.ctrl_generator import *
from generator.simple.simple_generator import *
import tensorflow as tf
import textwrap
import sys
CRED_FILE = "./AI-Adventure-2bb65e3a4e2f.json"


def play_unconstrained():
    generator = SimpleGenerator()
    prompt = get_story_start("classic")
    context = get_context("classic")
    story_manager = UnconstrainedStoryManager(generator)
    story_manager.start_new_story(prompt, context=context)

    print("\n")
    print(context)
    print(str(story_manager.story))
    while True:
        action = input("> ")

        if action != "":
            action = action.strip()

            action = action[0].lower() + action[1:]

            if action[-1] == "." or action[-1] == "?" or action[-1] == "!":
                action = action[:-1]
            if "you " == action.lower()[0:4]:
                action = action[4:]
            if "i " == action.lower()[0:2]:
                action = action[2:]

            action = " You " + action + ". "
            action = remove_profanity(action)
            action = first_to_second_person(action)

        result = story_manager.act(action)
        print("\n\n" + action + result)


if __name__ == '__main__':
    play_unconstrained()




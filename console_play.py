import os
from story.utils import *
from google.cloud import storage
import json
from story.story_manager import *
from generator.web.web_generator import *
import tensorflow as tf
import textwrap


# Set the key
def console_print(str):
    LINE_WIDTH=80
    print((textwrap.fill(str, 80)))


if __name__ == '__main__':
    generator = WebGenerator("./AI-Adventure-2bb65e3a4e2f.json")
    prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
    story_manager = UnconstrainedStoryManager(generator, prompt)

    console_print(str(story_manager.story))
    while(True):
        action = input("> ")
        action = "You " + action
        result = story_manager.act(action)
        console_print(action + result)




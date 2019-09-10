import os
from story.utils import *
from google.cloud import storage
import json
from story.story_manager import *
from generator.tf_local.generator_local import *
import tensorflow as tf

if __name__ == '__main__':

    sess = tf.Session()
    generator = LocalGenerator(sess)
    prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
    story_manager = UnconstrainedStoryManager(generator, prompt)
    print(story_manager.story)
    while(True):
        action = input("> ")
        action = "You " + action
        print(action)
        result = story_manager.act(action)
        print(result)




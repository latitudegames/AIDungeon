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


def play_unconstrained():
    generator = WebGenerator("./AI-Adventure-2bb65e3a4e2f.json")
    prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
    story_manager = UnconstrainedStoryManager(generator, prompt)

    console_print(str(story_manager.story))
    while (True):
        action = input("> ")
        action = "You " + action
        result = story_manager.act(action)
        console_print(action + result)

    #
    #
    #
    # def act(self, action_choice):
    #
    #     action, result = self.possible_action_results[action_choice]
    #     self.story.add_to_story(action, result)
    #     self.possible_action_results = self.get_action_results()
    #     return result, self.possible_action_results
    #
    # def story_context(self):
    #     return self.story.latest_result()
    #
    # def get_action_results(self):
    #     return [self.generate_action_result(self.story_context(), phrase) for phrase in self.action_phrases]
    #
    # def generate_action_result(self, prompt, phrase):
    #     action = phrase + self.generator.generate(prompt + phrase)
    #     action_result = cut_trailing_sentence(action)
    #
    #     action, result = split_first_sentence(action_result)
    #     result = story_replace(action_result)
    #     action = action_replace(action)
    #
    #     return action, result

def play_constrained():
    generator = WebGenerator("./AI-Adventure-2bb65e3a4e2f.json")
    prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
    story_manager = ConstrainedStoryManager(generator, prompt)

    console_print(str(story_manager.story))
    possible_actions = story_manager.get_possible_actions()
    while (True):
        console_print("\nOptions:")
        for i, action in enumerate(possible_actions):
            console_print(str(i) + ") " + action)

        result = None
        while(result == None):
            action_choice = input("Which action do you choose? ")
            print("\n")
            result, possible_actions = story_manager.act(action_choice)

        console_print(result)


if __name__ == '__main__':
    play_constrained()




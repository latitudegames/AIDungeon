#!/usr/bin/env python3
import os
import sys
import time
import argparse

from generator.gpt2.gpt2_generator import *
from generator.human_dm import *
from play import *
from story.story_manager import *
from story.utils import *

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

parser = argparse.ArgumentParser("Play AIDungeon DM Mode")
parser.add_argument(
    "--cpu",
    action="store_true",
    help="Force using CPU instead of GPU."
)


class AIPlayer:
    def __init__(self, generator):
        self.generator = generator

    def get_action(self, prompt):
        return self.generator.generate_raw(prompt)


def play_dm(args):
    """
    Entry/main function for starting AIDungeon DM Mode

    Arguments:
        args (namespace): Arguments returned by the
                          ArgumentParser
    """

    console_print("Initializing AI Dungeon DM Mode")
    generator = GPT2Generator(force_cpu=args.cpu, temperature=0.9)

    story_manager = UnconstrainedStoryManager(HumanDM())
    (
        setting_key,
        character_key,
        name,
        character,
        setting_description,
    ) = select_game()

    if setting_key == "custom":
        context, prompt = get_custom_prompt()
    else:
        context, prompt = get_curated_exposition(
            setting_key, character_key, name, character, setting_description
        )
    console_print(context + prompt)
    story_manager.start_new_story(prompt, context=context, upload_story=False)

    player = AIPlayer(generator)

    while True:
        action_prompt = story_manager.story_context() + "What do you do next? \n> You"
        action = player.get_action(action_prompt)
        print("\n******DEBUG FULL ACTION*******")
        print(action)
        print("******END DEBUG******\n")
        action = action.split("\n")[0]
        punc = action.rfind(".")
        if punc > 0:
            action = action[: punc + 1]
        shown_action = "> You" + action
        console_print(second_to_first_person(shown_action))
        story_manager.act(action)


if __name__ == "__main__":
    args = parser.parse_args()
    play_dm(args)

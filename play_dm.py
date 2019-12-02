from story.story_manager import *
from generator.human_dm import *
from generator.gpt2.gpt2_generator import *
from story.utils import *
from termios import tcflush, TCIFLUSH
from play import *
import time, sys, os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

class AIPlayer:

    def __init__(self, generator):
        self.generator = generator

    def get_action(self, prompt):
        return self.generator.generate_raw(prompt)

def play_dm():
    generator = GPT2Generator()
    story_manager = UnconstrainedStoryManager(HumanDM())
    context, prompt = select_game()
    console_print(context + prompt)
    story_manager.start_new_story(prompt, context=context, upload_story=False)

    player = AIPlayer(generator)

    while True:
        action_prompt = story_manager.story_context() + "\n> You "
        action = player.get_action(action_prompt)
        action = action.split("\n")[0]
        console_print(action)
        story_manager.act(action)




if __name__ == '__main__':
    play_dm()



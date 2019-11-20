from story.story_manager import *
from generator.gpt2.gpt2_generator import *
from story.utils import *
from story.custom_story import *
from termios import tcflush, TCIFLUSH
import time,sys

def select_game():
    print("Which game would you like to play?")
    options = ["zombies", "hospital", "apocalypse", "classic", "knight", "necromancer", "custom"]
    for i, option in enumerate(options):
        console_print(str(i) + ") " + option + "\n")

    choice = get_num_options(len(options))
    if options[choice] == "custom":
        context, prompt = make_custom_story()

    else:
        game = options[choice]
        prompt = get_story_start(game)
        context = get_context(game)

    return context, prompt

def instructions():
    text = "\nAI Dungeon 2 Instructions:"
    text += '\n* Enter actions starting with a verb ex. "go to the tavern" or "attack the orc."'
    text += '\n* If you want to say something then enter \'say "(thing you want to say)"\''
    text += '\n* Finally if you want to end your game and start a new one just enter "restart" for any action. '
    return text

def play_aidungeon_2():

    save_story = input("Help improve AIDungeon by enabling story saving? (Y/n) ")
    if save_story.lower() in ["no", "No", "n"]:
        upload_story = False
    else:
        upload_story = True

    print("\nInitializing AI Dungeon! (This might take a few minutes)\n")
    generator = GPT2Generator()
    story_manager = UnconstrainedStoryManager(generator)
    print("\n\n\n\n")

    with open('opening.txt', 'r') as file:
        starter = file.read()
    print(starter)

    while True:

        if story_manager.story != None:
            del story_manager.story

        print("\n\n")
        context, prompt = select_game()
        console_print(instructions())
        print("\nGenerating story...")

        story_manager.start_new_story(prompt, context=context, upload_story=upload_story)

        print("\n")
        console_print(context + str(story_manager.story))
        while True:
            tcflush(sys.stdin, TCIFLUSH)
            action = input("> ")
            if action == "restart":
                break
            elif action == "quit":
                exit()

            if action != "" and action.lower() != "continue":
                action = action.strip()

                action = first_to_second_person(action)

                if "You" not in action:
                    action = "You " + action

                if action[-1] not in [".", "?", "!"]:
                    action = action + "."

                action = "\n> " + action + "\n"
                # action = remove_profanity(action)
                #action = first_to_second_person(action)

            result = "\n" + story_manager.act(action)

            if player_died(result):
                console_print(result + "\nGAME OVER")
                break
            elif player_won(result):
                console_print(result + "\n CONGRATS YOU WIN")
                break
            else:
                console_print(result)


if __name__ == '__main__':
    play_aidungeon_2()


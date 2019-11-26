from story.story_manager import *
from generator.gpt2.gpt2_generator import *
from story.utils import *
from termios import tcflush, TCIFLUSH
import time, sys, os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

def select_game():
    with open(YAML_FILE, 'r') as stream:
        data = yaml.safe_load(stream)

    print("Pick a setting.")
    settings = data["settings"].keys()
    for i, setting in enumerate(settings):
        print_str = str(i) + ") " + setting
        if setting == "fantasy":
            print_str += " (recommended)"
        else:
            print_str += " (experimental)"
        console_print(print_str)
    console_print(str(len(settings)) + ") custom (for advanced players)")
    choice = get_num_options(len(settings)+1)

    if choice == len(settings):

        console_print("Enter a sentence or two that describes the context of who your character is. Ex. ' " +
                        "You are a knight living in the king of Larion. You have a sword and shield. '")
        context = input("Context: ")
        console_print("Enter the first couple sentences to start your adventure off. Ex. " +
                       "'You enter the forest searching for the dragon and see' ")
        prompt = input("Starting Prompt: ")
        return context, prompt

    setting_key = list(settings)[choice]

    print("\nPick a character")
    characters = data["settings"][setting_key]["characters"]
    for i, character in enumerate(characters):
        console_print(str(i) + ") " + character)
    character_key = list(characters)[get_num_options(len(characters))]

    name = input("\nWhat is your name? ")
    setting_description = data["settings"][setting_key]["description"]
    character = data["settings"][setting_key]["characters"][character_key]

    context = "You are " + name + ", a " + character_key + " " + setting_description + \
              "You have a " + character["item1"] + " and a " + character["item2"] + ". "
    prompt_num = np.random.randint(0, len(character["prompts"]))
    prompt = character["prompts"][prompt_num]

    return context, prompt

def instructions():
    text = "\nAI Dungeon 2 Instructions:"
    text += '\n* Enter actions starting with a verb ex. "go to the tavern" or "attack the orc."'
    text += '\n* To speak enter \'say "(thing you want to say)"\' or just "(thing you want to say)" '
    text += '\n* Enter "revert" for any action if you want to undo the last action and result.'
    text += '\n* Finally if you want to end your game and start a new one just enter "restart" for any action. '
    return text

def play_aidungeon_2():

    save_story = input("Help AIDungeon by letting us store your adventure to improve the model? (Y/n) ")
    if save_story.lower() in ["no", "No", "n"]:
        upload_story = False
    else:
        upload_story = True

    print("\nInitializing AI Dungeon! (This might take a few minutes)\n")
    generator = GPT2Generator()
    story_manager = UnconstrainedStoryManager(generator)
    print("\n")

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
            elif action == "revert":

                if len(story_manager.story.actions) is 0:
                    console_print("You can't go back any farther. ")
                    continue

                story_manager.story.actions = story_manager.story.actions[:-1]
                story_manager.story.results = story_manager.story.results[:-1]
                console_print("Last action reverted. ")
                if len(story_manager.story.results) > 0:
                    console_print(story_manager.story.results[-1])
                else:
                    console_print(story_manager.story.story_start)
                continue
            elif action[0] == '"':
                action = "You say " + action

            elif action != "":
                action = action.strip()
                action = action[0].lower() + action[1:]

                action = first_to_second_person(action)

                if "You" not in action:
                    action = "You " + action

                if action[-1] not in [".", "?", "!"]:
                    action = action + "."

                action = "\n> " + action + "\n"

            result = "\n" + story_manager.act(action)

            if player_won(result):
                console_print(result + "\n CONGRATS YOU WIN")
                break
            elif player_died(result):
                action = "> You die."
                final_result = story_manager.act(action)
                console_print(result + final_result)
            else:
                console_print(result)


if __name__ == '__main__':
    play_aidungeon_2()


from story.utils import *
import numpy as np

YAML_FILE = "story/story_data.yaml"


def make_custom_story():

    with open(YAML_FILE, 'r') as stream:
        data = yaml.safe_load(stream)["custom"]

    print("Pick a setting.")
    settings = data["settings"].keys()
    for i, setting in enumerate(settings):
        console_print(str(i) + ") " + setting)
    setting_key = list(settings)[get_num_options(len(settings))]

    print("Pick a character")
    characters = data["settings"][setting_key]["characters"]
    for i, character in enumerate(characters):
        console_print(str(i) + ") " + character)
    character_key = list(characters)[get_num_options(len(characters))]

    name = input("What is your name? ")
    setting_description = data["settings"][setting_key]["description"]
    character = data["settings"][setting_key]["characters"][character_key]

    context = "You are " + name + ", a " + character_key + " " + setting_description + \
              "You have a " + character["item1"] + " and a " + character["item2"] + ". "
    prompt_num = np.random.randint(0,len(character["prompts"]))
    prompt = character["prompts"][prompt_num]

    return context, prompt

if __name__=='__main__':
    c, p = make_custom_story()
    print(c)
    print(p)

    # print("Pick a setting.")
    # for i, setting in enumerate(settings):
    #     console_print(str(i) + ") " + setting)
    # setting_choice = get_num_options(len(settings))
    #
    #
    #
    # print("")
    # options = ["zombies", "hospital", "peasant", "apocalypse", "classic", "knight", "necromancer"]
    # for i, option in enumerate(options):
    #     console_print(str(i) + ") " + option + ": " + get_context(option) + "\n")
    #
    # choice = get_num_options(len(options))
    # return options[choice]
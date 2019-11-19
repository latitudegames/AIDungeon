from story.story_manager import *
from generator.gpt2.gpt2_generator import *

def console_print(text, width=75):
    last_newline = 0
    i = 0
    while i < len(text):
        if text[i] == "\n":
            last_newline = 0
        elif last_newline > width and text[i] == " ":
            text = text[:i] + "\n" + text[i:]
            last_newline = 0
        else:
            last_newline += 1
        i += 1
    print(text)


def get_num_options(num):

    while True:
        choice = input("Which do you choose? ")
        try:
            result = int(choice)
            if result >= 0 and result < num:
                return result
            else:
                print("Error invalid choice. ")
        except ValueError:
            print("Error invalid choice. ")


def select_game():
    print("Which game would you like to play?")
    options = ["zombies", "hospital", "peasant", "apocalypse", "classic", "knight", "necromancer", "vague"]
    for i, option in enumerate(options):
        console_print(str(i) + ") " + option + ": " + get_context(option) + "\n")

    choice = get_num_options(len(options))
    return options[choice]

def instructions():
    text = "AI Dungeon 2 Instructions:"
    text += '\n* Enter actions starting with a verb ex. "go to the tavern" or "attack the orc."'
    text += '\n* If you want to say something then enter \'say "(thing you want to say)"\'.'
    text += '\n* You can also just press enter with no action if you want to let the story continue.'
    text += '\n* Finally if you want to end your game and start a new one just enter "restart" for any action. '
    return text

def play_aidungeon_2():


    print("Initializing AI Dungeon! (This might take a few minutes)")
    generator = GPT2Generator()
    story_manager = UnconstrainedStoryManager(generator)
    print("\n\n\n\n")

    with open('opening.txt', 'r') as file:
        starter = file.read()
    print(starter)

    while True:

        print("\n\n")
        game = select_game()
        console_print(instructions())
        prompt = get_story_start(game)
        context = get_context(game)
        story_manager.start_new_story(prompt, context=context)


        print("\n")
        console_print(context + "\n\n" + str(story_manager.story))
        while True:
            action = input("> ")
            if action == "restart":
                break

            if action != "":
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
            else:
                console_print(result)


if __name__ == '__main__':
    play_aidungeon_2()


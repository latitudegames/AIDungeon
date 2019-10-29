from adventure import load_advent_dat
from adventure.game import Game
import re



fail_phrases = ["I SEE NO ",
                "I DON'T KNOW HOW TO APPLY THAT",
                "REQUIRES", "GOOD TRY, BUT THAT",
                "THERE IS NO WAY TO GO THAT DIRECTION",
                "THERE IS NOTHING HERE TO ",
                "SORRY, BUT I NO LONGER SEEM TO REMEMBER HOW IT WAS YOU GOT",
                "BREAK WHAT",
                "OKAY, FROM NOW ON I'LL ONLY DESCRIBE A PLACE IN FULL THE FIRST TIME",
                "WHAT?",
                "I DON'T KNOW WHERE",
                "THERE IS NOTHING HERE WITH",
                "I AM UNSURE HOW YOU ARE FACING",
                "WHICH WAY?",
                "IT WOULD BE ADVISABLE TO USE THE EXIT",
                "DIGGING WITHOUT A SHOVEL IS QUITE IMPRACTICAL",
                "YOU HAVE NO",
                "OK",
                "WHAT'S THE MATTER",
                "NOTHING HAPPENS",
                "YOU AREN'T CARRYING IT",
                "I DON'T KNOW HOW",
                "I DON'T KNOW THAT WORD",
                "I DON'T UNDERSTAND THAT",
                "YOU CAN'T BE SERIOUS",
                "DON'T BE RIDICULOUS"]

def failed(text):
    for fail_phrase in fail_phrases:
        if fail_phrase in text:
            return True

    return False

def get_possible_lines(commands, objects):
    lines = []
    for command in commands:
        for object in objects:
            lines.append(command + " " + object)

    return lines + commands

def save_game(game, file):
    print(game.do_command(["save", file]))

def load_game(game, file):
    game.resume(file)

fp = open('verbs.txt', 'r')
commands = []
for line in fp:
    commands.append(line[:-1])

fp = open('objects.txt', 'r')
objects = []
for line in fp:
    if line[:-1] not in commands:
        objects.append(line[:-1])

possible_lines = get_possible_lines(commands, objects)

game = Game()
load_advent_dat(game)
game.start()
print(game.do_command("no"))
successes = 0
save_game(game, "file")
while not game.is_finished:

    for i, line in enumerate(possible_lines[:]):
        load_game(game, "file")
        action = re.findall(r'\w+', line)
        result = game.do_command(action)
        if "ARE YOU TRYING TO" in result:
            game.do_command("no")
            continue
        if failed(result):
            # print("FAILED: ", " ".join(action))
            # print(result)
            continue
        else:
            print("> ", " ".join(action))
            print(result)
            successes += 1
            save_game(game, "file" + str(i))

    print("Successes is ", successes, " out of ", len(possible_lines))
    break

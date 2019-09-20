import re
import yaml

YAML_FILE = "story/story_data.yaml"


def get_story_start(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["prompts"][key]


def get_action_verbs(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["action_verbs"][key]

# TODO add capital words to remove words
def remove_profanity(text):
    remove_words = ["fuck", "Fuck", "shit", "rape", "bastard", "bitch"]
    for word in remove_words:
        text = text.replace(word, "****")
        
    return text


def all_replace(text):
    text = first_to_second_person(text)
    text = text.replace("#","")
    
    text = remove_profanity(text)
    
    return text
    
    
def action_replace(text):
    return all_replace(text)
    
    
def story_replace(text):
    return all_replace(text)
    
    
def split_first_sentence(text):
    first_period = text.find('.')
    first_exclamation = text.find('!')
    
    if first_exclamation < first_period and first_exclamation > 0:
        split_point = first_exclamation+1
    elif first_period > 0:
        split_point = first_period+1
    else:
        split_point = text[0:20]
        
    return text[0:split_point], text[split_point:]

    
def cut_trailing_sentence(text):
    last_period = text.rfind('.')
    last_exclamation = text.rfind('!')
    
    if last_exclamation > last_period:
        text = text[0:last_exclamation+1]
    elif last_period > 0:
        text = text[0:last_period+1]

    return text


def replace_outside_quotes(text, current_word, repl_word):

    reg_expr = re.compile(current_word + '(?=([^"]*"[^"]*")*[^"]*$)')

    output = reg_expr.sub(repl_word, text)
    return output


first_to_second_mappings = [
    ("I'm ", "you're "),
    ("I am ", "you are "),
    ("I ", "you "),
    ("I've ", "You've "),
    ("my ", "your "),
    ("My ", "Your "),
    ("we ","you "),
    ("We ","You "),
    (" mine"," yours"),
    (" me ", " you "),
    (" me.", " you."),
    (" us ", " you "),
    (" us.", " you."),
    (" our", " your")
]

second_to_first_mappings = [
    ("You're ", "I'm "),
    ("you're ", "I'm "),
    ("Your ", "My "),
    ("your ", "my "),
    ("you are ", "I am "),
    ("You are ", "I am "),
    ("You ", "I "),
    ("you ", "I "),
    (" you.", " me."),
]

def capitalize_helper(string):
    string_list = list(string)
    string_list[0] = string_list[0].upper()
    return "".join(string_list)


def capitalize_first_letters(text):
    first_letters_regex = re.compile(r'((?<=[\.\?!]\s)(\w+)|(^\w+))')

    def cap(match):
        return (capitalize_helper(match.group()))

    result = first_letters_regex.sub(cap, text)
    return result


def first_to_second_person(text):
    for pair in first_to_second_mappings:
        text = replace_outside_quotes(text, pair[0], pair[1])

    return capitalize_first_letters(text)


def second_to_first_person(text):
    for pair in second_to_first_mappings:
        text = replace_outside_quotes(text, pair[0], pair[1])

    return capitalize_first_letters(text)


possible_verbs = ["ask", "go", "run", "open", "look", "walk", "make", "try", "say", "tell", "attack", "use", "turn", "fight", "scream", "yell"]

def get_possible_verbs():
    return possible_verbs

if __name__ == '__main__':
    f = open("test.txt", "r")
    test_text = f.read()

    print("Text is \n\n",test_text)

    print("First person: ")
    converted = second_to_first_person(test_text)
    print(converted)

    print("Back to second person: ")
    print(first_to_second_person(converted))
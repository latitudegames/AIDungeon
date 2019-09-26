import re
import yaml

YAML_FILE = "story/story_data.yaml"

from profanityfilter import ProfanityFilter
pf = ProfanityFilter()

def get_story_start(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["prompts"][key]


def get_action_verbs(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["action_verbs"][key]


def get_ctrl_verbs(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["ctrl_verbs"][key]


def get_rooms(key):
    with open(YAML_FILE, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded["rooms"][key]


def remove_profanity(text):
    return pf.censor(text)


def cut_trailing_quotes(text):
    num_quotes = text.count('"')
    if num_quotes % 2 is 0:
        return text
    else:
        final_ind = text.rfind('"')
        return text[:final_ind]

    
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

    current_word = current_word.replace(".", "\.")

    reg_expr = re.compile(current_word + '(?=([^"]*"[^"]*")*[^"]*$)')

    output = reg_expr.sub(repl_word, text)
    return output
    

def capitalize(word):
    return word[0].upper() + word[1:]
    

def mapping_variation_pairs(mapping):
    mapping_list = []
    mapping_list.append((" " + mapping[0]+" ", " " + mapping[1]+" "))
    mapping_list.append((" " + capitalize(mapping[0]) + " ", " " + capitalize(mapping[1]) + " "))
    mapping_list.append((" " + mapping[0]+",", " " + mapping[1]+","))
    mapping_list.append((" " + mapping[0]+".", " " + mapping[1]+"."))
    mapping_list.append((" " + mapping[0]+"?", " " + mapping[1]+"?"))
    mapping_list.append((" " + mapping[0]+"!", " " + mapping[1]+"!"))
    return mapping_list


first_to_second_mappings = [
    ("I'm", "you're"),
    ("I am", "you are"),
    ("I", "you"),
    ("I've", "You've"),
    ("my", "your"),
    ("we","you"),
    ("we're", "you're"),
    ("mine","yours"),
    ("me", "you"),
    ("us", "you"),
    ("our", "your")
]

second_to_first_mappings = [
    ("you're", "I'm"),
    ("your ", "my "),
    ("you are", "I am"),
    ("you", "I"),
    ("you", "me")
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
    print("\nF_TO_S First person text:")
    print(text)
    for pair in first_to_second_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            text = replace_outside_quotes(text, variation[0], variation[1])

    return capitalize_first_letters(text)
    print("\nF_TO_S second person text:")
    print(text)

def second_to_first_person(text):
    print("\nS_TO_F second person text:")
    print(text)
    
    for pair in second_to_first_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            text = replace_outside_quotes(text, variation[0], variation[1])

    print("\nS_TO_F first person text:")
    print(text)
    return capitalize_first_letters(text)


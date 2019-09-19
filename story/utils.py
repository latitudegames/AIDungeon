import re


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

    reg_expr = '[^"]+"|(' + current_word + ')'

    output = re.sub(reg_expr, repl_word, text)
    return output


first_to_second_mappings = [
    ("I am", "you are"),
    ("I ", "you "),
    ("I've", "You've"),
    ("my", "your"),
    ("we ","you "),
    ("We ","You "),
    (" mine"," yours"),
]

second_to_first_mappings = [
    ("Your", "My"),
    ("your", "my"),
    ("you are", "I am"),
    ("You are", "I am"),
    ("You", "I"),
    ("you", "I"),
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

if __name__ == '__main__':
    test_text = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"
    print("First person: ")
    converted = second_to_first_person(test_text)
    print(converted)

    print("Back to second person: ")
    print(first_to_second_person(converted))
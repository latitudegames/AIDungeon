
"""
replacements:

    stories only:
        "you will" with "you"
        "go to" with "you go to"

    All
        "punctuation with no space. add a space
        "remove any # and - and _'s

"""


def remove_profanity(text):
    remove_words = ["fuck", "Fuck", "shit", "rape", "bastard", "bitch"]
    for word in remove_words:
        text = text.replace(word, "****")
        
    return text
    
def all_replace(text):
    text = text.replace("I ","you ")
    text = text.replace("we ","you ")
    text = text.replace("We ","You ")
    text = text.replace(" mine"," yours")
    text = text.replace("#","")
    
    text = remove_profanity(text)
    
    return text
    
    
def action_replace(text):
    return all_replace(text)
    
    
def story_replace(text):
    return all_replace(text)


def text_replace(text):
# Replace certain words
    text = text.replace("I ","you ")
    text = text.replace("we ","you ")
    text = text.replace("We ","You ")
    text = text.replace(" mine"," yours")
    text = text.replace("kill you", "hurt you")
    text = text.replace("[","")
    text = text.replace("]","")
    return text
    
    
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

    
def all_but_first(text):
    first_period = text.find('.')
    first_exclamation = text.find('!')
    
    if first_exclamation < first_period and first_exclamation > 0:
        text = text[first_exclamation+1:]
    elif first_period > 0:
        text = text[first_period+1:]
    else:
        return text[20:]
        
    return text
    
    
def cut_trailing_sentence(text):
    last_period = text.rfind('.')
    last_exclamation = text.rfind('!')
    
    if last_exclamation > last_period:
        text = text[0:last_exclamation+1]
    elif last_period > 0:
        text = text[0:last_period+1]

    return text
        

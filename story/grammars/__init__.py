
import json

import tracery
from tracery.modifiers import base_english


def gen(key, rules):
    grammar = tracery.Grammar(rules)
    grammar.add_modifiers(base_english)
    return grammar.flatten(f"#{key}#")


def noble(key):
    """
    Provides a randomized prompt according to the grammar rules in fantasy_rules.json
    """
    with open('story/grammars/fantasy_rules.json', 'r') as f:
        rules = json.load(f)

    prompt = gen(f"noble_{key}", rules)
    return prompt


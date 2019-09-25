from story.utils import *
from other.cacher import *
import json


class Story():

    def __init__(self, story_start, seed=None, game_state=None):
        self.story_start = story_start

        # list of actions. First action is the prompt length should always equal that of story blocks
        self.actions = []

        # list of story blocks first story block follows prompt and is intro story
        self.results = []

        # Only needed in constrained/cached version
        self.seed = seed
        self.choices = []
        self.possible_action_results = []

        if game_state is None:
            game_state = dict()
        self.game_state = game_state


    def initialize_from_json(self, json_string):
        story_dict = json.loads(json_string)
        self.story_start = story_dict["story_start"]
        self.seed = story_dict["seed"]
        self.actions = story_dict["actions"]
        self.results = story_dict["results"]
        self.choices = story_dict["choices"]
        self.possible_action_results = story_dict["possible_action_results"]
        self.game_state = story_dict["game_state"]

    def add_to_story(self, action, story_block):
        self.actions.append(action)
        self.results.append(story_block)

    def latest_result(self):
        if len(self.results) > 1:
            return self.results[-2] + self.actions[-1] + self.results[-1]
        elif len(self.results) == 1:
            return self.story_start + self.results[-1]
        else:
            return self.story_start

    def __str__(self):
        story_list = [self.story_start]
        for i in range(len(self.results)):
            story_list.append(self.actions[i])
            story_list.append(self.results[i])

        return "".join(story_list)

    def to_json(self):
        story_dict = {}
        story_dict["story_start"] = self.story_start
        story_dict["seed"] = self.seed
        story_dict["actions"] = self.actions
        story_dict["results"] = self.results
        story_dict["choices"] = self.choices
        story_dict["possible_action_results"] = self.possible_action_results
        story_dict["game_state"] = self.game_state


        return json.dumps(story_dict)

class StoryManager():

    def __init__(self, generator):
        self.generator = generator
        
    def start_new_story(self, story_prompt, game_state=None):
        block = self.generator.generate(story_prompt)
        block = cut_trailing_sentence(block)
        self.story = Story(story_prompt + block, game_state=None)
        return self.story
    
    def load_story(self, story, from_json=False):
        if from_json:
            self.story = Story("")
            self.story.initialize_from_json(story)
        else:
            self.story = story
        return str(story)

    def json_story(self):
        return self.story.to_json()

    def story_context(self):
        return self.story.latest_result()


class UnconstrainedStoryManager(StoryManager):

    def act(self, action_choice):
        result = self.generate_result(action_choice)
        self.story.add_to_story(action_choice, result)
        return result

    def generate_result(self, action):
        block = self.generator.generate(self.story_context() + action)
        block = cut_trailing_sentence(block)
        return block


class ConstrainedStoryManager(StoryManager):

    def __init__(self, generator, action_verbs_key="classic"):
        super().__init__(generator)
        self.action_phrases = get_action_verbs(action_verbs_key)

    def start_new_story(self, story_prompt, game_state=None):
        super().start_new_story(story_prompt, game_state=game_state)
        self.story.possible_action_results = self.get_action_results()
        
        return self.story.story_start

    def load_story(self, story, from_json=False):
        story_string = super().load_story(story, from_json=from_json)
        return story_string

    def get_possible_actions(self):
        if self.story.possible_action_results is None:
            self.story.possible_action_results = self.get_action_results()

        return [action_result[0] for action_result in self.story.possible_action_results]

    def act(self, action_choice_str):

        try:
            action_choice = int(action_choice_str)
        except:
            print("Error invalid choice.")
            return None, None

        if action_choice < 0 or action_choice >= len(self.action_phrases):
            print("Error invalid choice.")
            return None, None

        self.story.choices.append(action_choice)
        action, result = self.story.possible_action_results[action_choice]
        self.story.add_to_story(action, result)
        self.story.possible_action_results = self.get_action_results()
        return result, self.get_possible_actions()

    def get_action_results(self):
        return [self.generate_action_result(self.story_context(), phrase) for phrase in self.action_phrases]

    def generate_action_result(self, prompt, phrase, options=None):
        if options is None:
            options = {}

        action = phrase + " " + self.generator.generate(prompt + " " + phrase, options)
        action_result = cut_trailing_sentence(action)

        action, result = split_first_sentence(action_result)

        return action, result

possible_rooms = ["hospital lobby", "hospital operating room", "hospital hallway", "the hospital parking lot"]

class CTRLStoryManager(ConstrainedStoryManager):
    def __init__(self, generator, action_verbs_key="anything"):
        super().__init__(generator, action_verbs_key)

    def start_new_story(self, story_prompt, game_state=None):
        game_state = {"current_room": "hospital_lobby"}
        super().start_new_story(story_prompt, game_state=game_state)

        return self.story.story_start

    def get_constrained_movement_options(self):
        options = {}
        options["word_whitelist"] = dict()
        options["word_whitelist"][0] = get_possible_verbs(type="movement")
        options["word_whitelist"][1] = ["to"]
        options["word_whitelist"][2] = ["the"]
        options["word_whitelist"][3] = \
            [room for room in possible_rooms if room is not self.story.game_state["current_room"]]
        options["word_whitelist"][4] = ["and"]
        options["word_whitelist"][5] = ["see"]

        return options

    # def get_action_results(self):
    #
    #     used_verbs = []
    #     results = []
    #     for phrase in self.action_phrases:
    #         options = dict()
    #         options["word_blacklist"] = {0: used_verbs}
    #         options["word_whitelist"] = {0: get_possible_verbs()}
    #         result = self.generate_action_result(self.story_context(), phrase, options=options)
    #
    #         used_verb = result[0].split()[1]
    #         used_verbs.append(used_verb)
    #
    #         results.append(result)
    #     return results

    def get_action_results(self):

        results = []
        options = self.get_constrained_movement_options()
        for phrase in self.action_phrases:
            result = self.generate_action_result(self.story_context(), phrase, options=options)
            location = result[0].split()[3]
            options["word_whitelist"][3].remove(location)

            results.append(result)
        return results


class CachedStoryManager(ConstrainedStoryManager):

    def __init__(self, generator, credentials_file, action_verbs_key="classic"):
        super().__init__(generator, action_verbs_key=action_verbs_key)
        self.cacher = cacher(credentials_file)

    def start_new_story(self, prompt, seed=0):

        result = self.cacher.retrieve_from_cache(seed, [], "story")
        if result is not None:
            story_start = prompt + result
            self.story = Story(story_start, seed=seed)
        else:
            story_start = super().start_new_story(prompt)
            self.story.seed = seed
            self.cacher.cache_file(seed, [], story_start, "story")

        self.story.possible_action_results = None

        return story_start

    def get_action_results(self):

        response = self.cacher.retrieve_from_cache(self.story.seed, self.story.choices, "choices")

        if response is not None:
            action_results = json.loads(response)
        else:
            print("Not found in cache. Generating...")
            action_results = super().get_action_results()
            response = json.dumps(action_results)
            self.cacher.cache_file(self.story.seed, self.story.choices, response, "choices")

        return action_results



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
            return self.actions[-2] + self.results[-2] + self.actions[-1] + self.results[-1]
        elif len(self.results) >= 1:
            return self.story_start + self.actions[-1] + self.results[-1] 
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
        self.story = Story(story_prompt + block, game_state=game_state)
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
        self.cache = False
        self.cacher = None
        self.seed = None

    def enable_caching(self, credentials_file=None, seed=0, bucket_name="dungeon-cache"):
        self.cache = True
        self.cacher = Cacher(credentials_file, bucket_name)
        self.seed = seed

    def start_new_story(self, story_prompt, game_state=None):
        if self.cache:
            return self.start_new_story_cache(story_prompt, game_state=game_state)
        else:
            return self.start_new_story(story_prompt, game_state=game_state)

    def start_new_story_generate(self, story_prompt, game_state=None):
        super().start_new_story(story_prompt, game_state=game_state)
        self.story.possible_action_results = self.get_action_results()
        return self.story.story_start

    def start_new_story_cache(self, story_prompt, game_state=None):

        response = self.cacher.retrieve_from_cache(self.seed, [], "story")
        if response is not None:
            story_start = story_prompt + response
            self.story = Story(story_start, seed=self.seed)
            self.story.possible_action_results = self.get_action_results()
        else:
            story_start = self.start_new_story_generate(story_prompt, game_state=game_state)
            self.story.seed = self.seed
            self.cacher.cache_file(self.seed, [], story_start, "story")

        return story_start

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
        if self.cache:
            return self.get_action_results_cache()
        else:
            return self.get_action_results_generate()

    def get_action_results_generate(self):
        action_results = [self.generate_action_result(self.story_context(), phrase) for phrase in self.action_phrases]
        return action_results

    def get_action_results_cache(self):
        response = self.cacher.retrieve_from_cache(self.story.seed, self.story.choices, "choices")

        if response is not None:
            print("Retrieved from cache")
            return json.loads(response)
        else:
            print("Didn't receive from cache")
            action_results = self.get_action_results_generate()
            response = json.dumps(action_results)
            self.cacher.cache_file(self.story.seed, self.story.choices, response, "choices")
            return action_results

    def generate_action_result(self, prompt, phrase, options=None):

        action = phrase + " " + self.generator.generate(prompt + " " + phrase, options)
        action_result = cut_trailing_sentence(action)
        action, result = split_first_sentence(action_result)
        return action, result


class CTRLStoryManager(ConstrainedStoryManager):
    def __init__(self, generator, action_verbs_key="anything"):
        super().__init__(generator, action_verbs_key)

    def start_new_story(self, story_prompt, game_state=None):
        game_state = {"current_room": "lobby"}
        super().start_new_story(story_prompt, game_state=game_state)

        return self.story.story_start

    def get_constrained_movement_options(self):
        options = {}
        options["word_whitelist"] = dict()
        options["word_whitelist"][0] = get_ctrl_verbs("movement")
        options["word_whitelist"][1] = ["to"]
        options["word_whitelist"][2] = ["the"]
        options["word_whitelist"][3] = \
            [room for room in get_rooms("haunted_hospital") if room is not self.story.game_state["current_room"]]
        options["word_whitelist"][4] = ["and"]
        options["word_whitelist"][5] = ["see"]

        return options, 3

    def get_action_results_generate(self):
        results = []
        options, location_pos = self.get_constrained_movement_options()
        for phrase in self.action_phrases:
            result = self.generate_action_result(self.story_context(), phrase, options=options)
            location = result[0].split()[location_pos+1]
            options["word_whitelist"][location_pos].remove(location)

            results.append(result)
        return results

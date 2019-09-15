from story.utils import *


class Story():

    def __init__(self, story_start):

        self.story_start = story_start

        # list of actions. First action is the prompt length should always equal that of story blocks
        self.actions = []

        # list of story blocks first story block follows prompt and is intro story
        self.results = []

    def add_to_story(self, action, story_block):
        self.actions.append(action)
        self.results.append(story_block)

    def latest_result(self):
        if len(self.results) > 0:
            return self.results[-1]
        else:
            return ""

    def __str__(self):
        story_list = [self.story_start]
        for i in range(len(self.results)):
            story_list.append(self.actions[i])
            story_list.append(self.results[i])

        return "".join(story_list)


class UnconstrainedStoryManager():

    def __init__(self, generator, story_prompt):
        self.generator = generator

        block = self.generator.generate(story_prompt)
        block = cut_trailing_sentence(block)
        block = story_replace(block)
        story_start = story_prompt + block

        self.story = Story(story_start)

    def act(self, action_choice):

        result = self.generate_result(action_choice)
        self.story.add_to_story(action_choice, result)
        return result

    def story_context(self):
        return self.story.latest_result()

    def generate_result(self, action):
        block = self.generator.generate(self.story_context() + action)
        block = cut_trailing_sentence(block)
        block = story_replace(block)
        return block


class ConstrainedStoryManager():

    def __init__(self, generator, story_prompt):
        self.generator = generator
        self.action_phrases = ["You attack", "You tell", "You use", "You go"]
        block = self.generator.generate(story_prompt)
        block = cut_trailing_sentence(block)
        block = story_replace(block)
        story_start = story_prompt + block
        self.story = Story(story_start)
        self.possible_action_results = None

    def get_possible_actions(self):
        if self.possible_action_results is None:
            self.possible_action_results = self.get_action_results()

        return [action_result[0] for action_result in self.possible_action_results]

    def act(self, action_choice_str):

        try:
            action_choice = int(action_choice_str)
        except:
            print("Error invalid choice.")
            return None, None

        if action_choice < 0 or action_choice >= len(self.action_phrases):
            print("Error invalid choice.")
            return None, None

        action, result = self.possible_action_results[action_choice]
        self.story.add_to_story(action, result)
        self.possible_action_results = self.get_action_results()
        return result, self.get_possible_actions()

    def story_context(self):
        return self.story.latest_result()

    def get_action_results(self):
        return [self.generate_action_result(self.story_context(), phrase) for phrase in self.action_phrases]

    def generate_action_result(self, prompt, phrase):
        action = phrase + self.generator.generate(prompt + phrase)
        action_result = cut_trailing_sentence(action)

        action, result = split_first_sentence(action_result)
        result = story_replace(action_result)
        action = action_replace(action)

        return action, result

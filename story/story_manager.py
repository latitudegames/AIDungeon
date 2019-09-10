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

        return sum(story_list)


class UnconstrainedStoryGenerator():

    def __init__(self, generator, story_start):
        self.story = Story(story_start)
        self.generator = generator

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


class ConstrainedStoryGenerator():

    def __init__(self, generator, story_start):
        self.story = Story(story_start)
        self.generator = generator
        self.possible_action_results = self.get_action_results()
        self.action_phrases = ["You attack", "You tell", "You use", "You go"]

    def act(self, action_choice):

        action, result = self.possible_action_results[action_choice]
        self.story.add_to_story(action, result)
        self.possible_action_results = self.get_action_results()
        return result, self.possible_action_results

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

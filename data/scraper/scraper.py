from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
"""
format of tree is
dict {
    tree_id: tree_id_text
    context: context text?
    first_story_block
    action_results: [act_res1, act_res2, act_res3...]
}

where each action_result's format is:
dict{
    action: action_text
    result: result_text
    action_results: [act_res1, act_res2, act_res3...]
}
"""

class Scraper:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--binary=/path/to/other/chrome/binary")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920x1080")
        exec_path = "/usr/bin/chromedriver"
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=exec_path)
        self.max_depth = 10
        self.end_action = "End Game and Leave Comments"
        self.texts = set()

    def GoToURL(self, url):
        self.driver.get(url)
        time.sleep(0.5)

    def GetText(self):
        div_elements = self.driver.find_elements_by_css_selector("div")
        text = div_elements[3].text
        return text

    def GetLinks(self):
        return self.driver.find_elements_by_css_selector("a")

    def GoBack(self):
        self.GetLinks()[0].click()
        time.sleep(0.2)

    def ClickAction(self, links, action_num):
        links[action_num+4].click()
        time.sleep(0.2)

    def GetActions(self):
        return [link.text for link in self.GetLinks()[4:]]

    def NumActions(self):
        return len(self.GetLinks()) - 4

    def BuildTreeHelper(self, parent_story, action_num, depth, old_actions):
        depth += 1
        action_result = {}

        action = old_actions[action_num]
        print("Action is ", action)
        action_result["action"] = action

        links = self.GetLinks()
        if action_num+4 >= len(links):
            return None

        self.ClickAction(links, action_num)
        result = self.GetText()
        if result == parent_story or result in self.texts:
            self.GoBack()
            return None

        self.texts.add(result)
        print(len(self.texts))

        action_result["result"] = result

        actions = self.GetActions()
        action_result["action_results"] = []

        for i, action in enumerate(actions):
            if actions[i] != self.end_action and actions[i] != "Epilogue":
                sub_action_result = self.BuildTreeHelper(result, i, depth, actions)
                if action_result is not None:
                    action_result["action_results"].append(sub_action_result)

        self.GoBack()
        return action_result


    def BuildStoryTree(self, url):
        scraper.GoToURL(url)
        text = scraper.GetText()
        actions = self.GetActions()
        story_dict = {}
        story_dict["tree_id"] = url
        story_dict["context"] = ""
        story_dict["first_story_block"] = text
        story_dict["action_results"] = []

        for i, action in enumerate(actions):
            if action != self.end_action:
                action_result = self.BuildTreeHelper(text, i, 0, actions)
                if action_result is not None:
                    story_dict["action_results"].append(action_result)

        return story_dict

def save_tree(tree, filename):
    with open(filename, 'w') as fp:
        json.dump(tree, fp)

scraper = Scraper()

urls = ["http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10638",
        "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11246"]

tree = scraper.BuildStoryTree(urls[0])
save_tree(tree, "scraped_story.json")
print("done")

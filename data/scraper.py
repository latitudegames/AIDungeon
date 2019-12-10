import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        self.driver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=exec_path
        )
        self.max_depth = 10
        self.end_actions = {
            "End Game and Leave Comments",
            "Click here to End the Game and Leave Comments",
            "See How Well You Did (you can still back-page afterwards if you like)",
            "You have died.",
            "You have died",
            "Epilogue",
            "Save Game",
            "Your quest might have been more successful...",
            "5 - not the best, certainly not the worst",
            "The End! (leave comments on game)",
            "6 - it's worth every cent",
            "You do not survive the journey to California",
            "Quit the game.",
            "7 - even better than Reeses' Cups®",
            "8 - it will bring you enlightenment",
            "End of game! Leave a comment!",
            "Better luck next time",
            "click here to continue",
            "Rating And Leaving Comments",
            "You do not survive your journey to California",
            "Your Outlaw Career has come to an end",
            "Thank you for taking the time to read my story",
            "You have no further part in the story, End Game and Leave Comments",
            "",
            "You play no further part in this story. End Game and Leave Comments",
            "drivers",
            "Alas, poor Yorick, they slew you well",
            "My heart bleeds for you",
            "To End the Game and Leave Comments click here",
            "Call it a day",
            "Check the voicemail.",
            "reset",
            "There's nothing you can do anymore...it's over.",
            "To Be Continued...",
            "Thanks again for taking the time to read this",
            "If you just want to escape this endless story you can do that by clicking here",
            "Boo Hoo Hoo",
            "End.",
            "Pick up some money real quick",
            "",
            "Well you did live a decent amount of time in the Army",
            "End Game",
            "You have survived the Donner Party's journey to California!",
        }
        self.texts = set()

    def GoToURL(self, url):
        self.texts = set()
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
        links[action_num + 4].click()
        time.sleep(0.2)

    def GetActions(self):
        return [link.text for link in self.GetLinks()[4:]]

    def NumActions(self):
        return len(self.GetLinks()) - 4

    def BuildTreeHelper(self, parent_story, action_num, depth, old_actions):
        depth += 1
        action_result = {}

        action = old_actions[action_num]
        print("Action is ", repr(action))
        action_result["action"] = action

        links = self.GetLinks()
        if action_num + 4 >= len(links):
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
            if actions[i] not in self.end_actions:
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
            if action not in self.end_actions:
                action_result = self.BuildTreeHelper(text, i, 0, actions)
                if action_result is not None:
                    story_dict["action_results"].append(action_result)
            else:
                print("done")

        return story_dict


def save_tree(tree, filename):
    with open(filename, "w") as fp:
        json.dump(tree, fp)


scraper = Scraper()

urls = [
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10638",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11246",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=54639",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7397",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8041",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11545",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7393",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=13875",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=37696",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=31013",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=45375",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=41698",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10634",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=42204",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=6823",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=18988",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10359",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=5466",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=28030",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=56515",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7480",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11274",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=53134",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=17306",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=470",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8041",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=23928",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10183",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=45866",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=60232",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=6376",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=36791",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=60128",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=52961",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=54011",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=34838",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=13349",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8038",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=56742",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=48393",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=53356",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10872",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7393",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=31013",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=43910",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=53837",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8098",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=55043",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=28838",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11906",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8040",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=2280",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=31014",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=43744",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=44543",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=56753",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=36594",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=15424",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8035",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10524",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=14899",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=9361",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=28030",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=49642",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=43573",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=38025",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7480",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7567",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=60747",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10359",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=31353",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=13875",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=56501",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=38542",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=42204",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=43993",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=1153",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=24743",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=57114",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=52887",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=21879",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=16489",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=53186",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=34849",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=26752",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=7094",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=8557",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=45225",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=4720",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=51926",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=45375",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=27234",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=60772",
]

for i in range(50, len(urls)):
    print("****** Extracting Adventure ", urls[i], " ***********")
    tree = scraper.BuildStoryTree(urls[i])
    save_tree(tree, "stories/story" + str(41 + i) + ".json")

print("done")

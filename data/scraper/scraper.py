from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


class Scraper:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--binary=/path/to/other/chrome/binary")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920x1080")
        exec_path = "/usr/bin/chromedriver"
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=exec_path)

    def GoToURL(self, url):
        self.driver.get(url)
        time.sleep(0.5)

    def GatherText(self):
        div_elements = self.driver.find_elements_by_css_selector("div")
        text = div_elements[3].text
        return text

    def GetLinks(self):
        return self.driver.find_elements_by_css_selector("a")

    def GoBack(self):
        self.GetLinks().click()

    def ClickAction(self, action_num):
        self.GetLinks()[action_num+4].click()


scraper = Scraper()
urls = ["http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10638",
        "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11246"]
scraper.GoToURL(urls[1])
scraper.ClickAction(0)
text = scraper.GatherText()
print("Done")
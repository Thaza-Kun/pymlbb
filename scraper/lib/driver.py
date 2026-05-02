from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class FireFox(webdriver.Firefox):
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("-profile")
        options.add_argument(
            r"/home/makmal-thaza/.mozilla/firefox/3jquypib.SeleniumUser"
        )

        super().__init__(options=options)

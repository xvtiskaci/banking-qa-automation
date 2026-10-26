import os
from selenium import webdriver


class BrowserFactory:

    @staticmethod
    def get_browser(browser="chrome"):
        name = browser.lower()
        headless = os.getenv("HEADLESS", "false").strip().lower() in {"true", "1", "yes"}

        if name == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
            return webdriver.Chrome(options=options)

        if name == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("-headless")
            return webdriver.Firefox(options=options)
        if name == "safari":
            if headless:
                raise ValueError("Safari headless mode is not supported by this framework")
            return webdriver.Safari()
        raise ValueError(f"Unsupported browser: {browser!r}")

# create by andy at 2022/4/1
# reference:

import platform

from selenium import webdriver
from selenium.webdriver.firefox.service import Service


def get_driver():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    if platform.system() == "Linux":
        driver_path = "driver/geckodriver"
    else:
        driver_path = "driver/geckodriver.exe"
    service = Service(driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    print(f"你正在使用{platform.system()}操作系统")
    return driver


if __name__ == '__main__':
    get_driver()

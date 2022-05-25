#!/usr/bin/env python

import selenium, sqlite3
from selenium import webdriver


def get_comic_link(date):
    driver = webdriver.Firefox()
    driver.get("https://www.gocomics.com/heathcliff/2021/04/19")
    
    comic_obj = driver.find_element_by_xpath('//img[contains(@alt, "Heathcliff Comic Strip for")]')
    comic_link = comic_obj.get_attribute("src")

    return comic_link


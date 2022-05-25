#!/usr/bin/env python

import selenium, sqlite3, datetime
from selenium import webdriver


def get_comic_link(day, month, year):
    # Start Firefox WebDriver instance
    driver = webdriver.Firefox()

    # Set and grab todays link
    link = f"""https://www.gocomics.com/heathcliff/{year}/{month}/{day}"""
    driver.get(link)
    
    # Grab the comic image link from the webpage
    comic_obj = driver.find_element_by_xpath('//img[contains(@alt, "Heathcliff Comic Strip for")]')
    comic_link = comic_obj.get_attribute("src")

    return comic_link

def main()

    # Get today's date
    date = datetime.datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")

    # Get today's comic link
    get_comic_link(day, month, year)

if __name__ == "__main__":
  main()

#!/usr/bin/env python

import sqlite3, datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def get_comic_link(day, month, year):
    # Start Firefox WebDriver instance and sert to headless
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    driver = webdriver.Firefox(options=firefox_options)

    # Set and grab todays link
    link = f"""https://www.gocomics.com/heathcliff/{year}/{month}/{day}"""
    driver.get(link)
    
    # Grab the comic image link from the webpage
    comic_obj = driver.find_element_by_xpath('//img[contains(@alt, "Heathcliff Comic Strip for")]')
    comic_link = comic_obj.get_attribute("src")

    driver.quit()

    return comic_link

def main():

    # Get today's date
    date = datetime.datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")

    # Get today's comic link
    comic_link = get_comic_link(day, month, year)

    print(comic_link)


if __name__ == "__main__":
  main()

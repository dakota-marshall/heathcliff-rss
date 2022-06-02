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

def database_save(date, url):

    # Create SQLite connection
    # This assumes the 'posts' table has been made with this schema ("date" TEXT, "img_url" TEXT)
    conn = sqlite3.connect('heathcliff.db')
    cursor = conn.cursor()

    # Query if date is already in DB
    cursor.execute(f"""SELECT * FROM posts WHERE date = '{date}'""")
    result = cursor.fetchall()
    
    # Return if we get anything back from the query
    if any(result):
        conn.close()
        return 1
    
    # Write new entry if not
    cursor.execute(f"""INSERT INTO posts (date, img_url) VALUES ('{date}', '{url}')""")
    conn.commit()
    conn.close()
    return 0

def main():

    # Get today's date
    date = datetime.datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")
    date_string = date.strftime("%Y-%m-%d")

    # Get today's comic link
    comic_link = get_comic_link(day, month, year)
    
    #Write URL to database
    database_save(date_string, comic_link)

    # Generate New RSS Post

if __name__ == "__main__":
  main()

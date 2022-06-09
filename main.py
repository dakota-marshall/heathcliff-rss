#!/usr/bin/env python

import sqlite3, datetime, threading
from email import utils
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def get_comic_link(day, month, year):
    # Start Firefox WebDriver instance and set to headless
    webdriver_url = "http://firefox:4444"
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Remote(command_executor=webdriver_url, options=firefox_options)

    # Set and grab todays link
    link = f"""https://www.gocomics.com/heathcliff/{year}/{month}/{day}"""
    driver.get(link)
    
    # Grab the comic image link from the webpage
    comic_obj = driver.find_element_by_xpath('//img[contains(@alt, "Heathcliff Comic Strip for")]')
    comic_link = comic_obj.get_attribute("src")

    driver.quit()

    return comic_link, link

def database_save(date, url, src_url):

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
    
    # Write new entry if noo
    # Generate an rfc 2822 timestamp for todays post
    rfc2822_date = utils.format_datetime(datetime.datetime.now())
    cursor.execute(f"""INSERT INTO posts (date, , rfc_2822_date, img_url, src_url) VALUES ('{date}', '{rfc2822_date}', '{url}', '{src_url}')""")
    conn.commit()
    conn.close()
    return 0

def query_comics():

    # Create SQLite connection
    # This assumes the 'posts' table has been made with this schema ("date" TEXT, "img_url" TEXT)
    conn = sqlite3.connect('heathcliff.db')
    cursor = conn.cursor()

    cursor.execute(f"""SELECT * FROM posts ORDER BY date DESC LIMIT 20""")
    result = cursor.fetchall()
    conn.close()

    return result

def generate_rss():
    
    # Set header and footer tags needed for the RSS Feed
    header_tags="""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
"""

    footer_tags="""</channel>
</rss>"""

    # Overly complex variable to get a properly formatted timestamp for the title
    build_date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4.0))).strftime("%a, %d %b %Y %X %Z")
    title = f"""<title>Heathcliff</title>
<link></link>
<description>Heathcliff by George Gately</description>
<lastBuildDate>{build_date}</lastBuildDate>
<generator>https://gitlab.com/dakota.marshall/heathcliff-rss</generator>
<language>en</language>
<image>
    <title>Heathcliff</title>
    <url>https://avatar.amuniversal.com/feature_avatars/recommendation_images/features/crhea/large_rec-201701251555.jpg</url>
    <link></link>
</image>
<copyright>Copyright George Gately</copyright>
<atom:link href="https://dakotamarshall.net/heathcliff.rss" rel="self" type="application/rss+xml"/>
"""

    # Get post list
    post_list = query_comics()

    # Overwrite the rss file with the header, then reopen the file and start appending the posts
    feed = open("heathcliff.rss", "w")
    feed.write(header_tags)
    feed.close
    feed = open("heathcliff.rss", "a+")
    feed.write(title)

    # Loop through each post and prep the data
    for post in post_list:
        date = post[0]
        rfc_date = post[1]
        img_url = post[2]
        src_url = post[3]

        post_text = f"""<item>
    <title><![CDATA[Heathcliff by George Gately for {date}]]></title>
    <link>{src_url}</link>
    <guid isPermaLink="false">heathcliff{date}</guid>
    <pubDate>{rfc_date}</pubDate>
    <description><![CDATA[<p>
<img src="{img_url}" alt="Heathcliff by George Gately on {date}" title="Heathcliff by George Gately on {date}">
</p>
<p>
<a href="{src_url}">Source</a> -
<a href="https://gitlab.com/dakota.marshall/heathcliff-rss">RSS Code</a>
</p>
]]></description>
</item>"""
        # Write post to file
        feed.write(post_text)
    
    # Finish off with writing the footer
    feed.write(footer_tags)
    feed.close()

def main_thread():
    # Generate a thread with a timer of 5hrs
    threading.Timer(18000, main_thread).start()

    # Get today's date
    date = datetime.datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")
    date_string = date.strftime("%Y-%m-%d")

    # Get today's comic link
    comic_link, src_link = get_comic_link(day, month, year)
    
    #Write URL to database
    database_save(date_string, comic_link, src_link)

    # Generate New RSS Post
    generate_rss()

def main():
    # Call main thread
    main_thread()

if __name__ == "__main__":
  main()

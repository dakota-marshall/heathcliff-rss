#!/usr/bin/env python

import os, datetime, threading, pymongo
from flask import Flask, Response
from email import utils
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

flask = Flask(__name__)

mongo_url = os.getenv('MONGODB_URL', 'mongodb://mongo:27017')
mongo_username = os.getenv('MONGODB_USERNAME', '')
mongo_password = os.getenv('MONGODB_PASSWORD', '')

# Establish a connection to the MongoDB server
client = pymongo.MongoClient(mongo_url)

# Select the database and collection to use
db = client["heathcliff"]
col = db["posts"]

def get_comic_link(day, month, year):
    # Start Firefox WebDriver instance and set to headless
    webdriver_url = "http://firefox:4444"
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Remote(command_executor=webdriver_url, options=firefox_options)

    # Set and grab todays link
    link = f"""https://www.gocomics.com/heathcliff/{year}/{month}/{day}"""
    driver.get(link)
    
    # Grab the comic image link from the webpage
    try:
        comic_obj = driver.find_element_by_xpath('//img[contains(@alt, "Heathcliff Comic Strip for")]')
        comic_link = comic_obj.get_attribute("src")
        driver.quit()
    except:
        print("ERROR: Error parsing for comic, post likely doesnt exist yet for today")
        return "error", "error"

    return comic_link, link

def database_save(date, url, src_url):

    # Prep JSON data
    data = {
        'date': date,
        'rfc_2822_date': rfc2822_date,
        'img_url': url,
        'src_url': src_url
    }

    # Write document to database if it does not already exist
    existing_post = col.find_one({'date': date})
    if not existing_post:
        col.insert_one(data)
    else:
        print(f"{date}: Post already found in database.")
        return 1

    print(f"{date}: Saved new post")
    return 0

def query_comics():
    result = []
    # Query all documents in the collection
    for post in col.find({}).sort([('date', pymongo.DESCENDING)]).limit(20):
        result.append(post)

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

    #

    # Overwrite the rss file with the header, then reopen the file and start appending the posts
    feed = open("heathcliff.rss", "w")
    feed.write(header_tags)
    feed.close
    feed = open("heathcliff.rss", "a+")
    feed.write(title)

    # Loop through each post and prep the data
    for post in post_list:
        post = post.to_dict()
        date = post['date']
        rfc_date = post['rfc_2822_date']
        img_url = post['img_url']
        src_url = post['src_url']

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

def rss_thread():

    # Get today's date
    date = datetime.datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")
    date_string = date.strftime("%Y-%m-%d")

    # Get today's comic link
    comic_link, src_link = get_comic_link(day, month, year)
    
    # Ensure that we got a valid link before continuing
    if comic_link != "error":
        #Write URL to database
        database_save(date_string, comic_link, src_link)
        
        # Generate New RSS Post
        generate_rss()

    # Generate another thread with a timer of 5hrs
    threading.Timer(18000, rss_thread).start()

@flask.route("/")
def give_feed():
    try:
        file = open('heathcliff.rss','r')
        rss = file.read()
        file.close()

        return Response(rss, mimetype='text/xml')
    except:
        print("ERROR: Error reading heathcliff.rss")
        return "Error Reading RSS Feed..."

if __name__ == "__main__":

    # Call rss thread
    threading.Thread(target=rss_thread).start()

    # Call flask thread
    threading.Thread(target=lambda: flask.run(host='0.0.0.0', port='80', debug=False, use_reloader=False)).start()


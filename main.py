#!/usr/bin/env python

import os, datetime, threading, firebase_admin
from email import utils
from firebase_admin import credentials
from firebase_admin import firestore
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

    # Connect to firestore
    firestore_db = firestore.client()

    # Generate an rfc 2822 timestamp for todays post
    rfc2822_date = utils.format_datetime(datetime.datetime.now())

    # Prep JSON data
    data = {
        u'date': date,
        u'rfc_2822_date': rfc2822_date,
        u'img_url': url,
        u'src_url': src_url
    }

    # Write document to DB if post does NOT exist
    existing_post = firestore_db.collection(u'posts').document(date).get()
    if not existing_post.exists:
        firestore_db.collection(u'posts').document(date).set(data)
    else:
        return 1

    return 0

def query_comics():

    # Connect to firestore
    firestore_db = firestore.client()

    # Query all documents in DB
    query = firestore_db.collection(u'posts').order_by(u'date', direction=firestore.Query.DESCENDING).limit(20)
    result = query.stream()

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

def main_thread():
    # Generate a thread with a timer of 5hrs
    threading.Timer(18000, main_thread).start()

    # Generate Firebase cert JSON from environment variables
    firebase_config = {
        "type": os.environ[u'FIREBASE_TYPE'],
        "project_id": os.environ[u'FIREBASE_PROJECT_ID'],
        "private_key_id": os.environ[u'FIREBASE_PRIV_KEY_ID'],
        "private_key": os.environ[u'FIREBASE_PRIV_KEY'],
        "client_email": os.environ[u'FIREBASE_CLIENT_EMAIL'],
        "client_id": os.environ[u'FIREBASE_CLIENT_ID'],
        "auth_uri": os.environ[u'FIREBASE_AUTH_URI'],
        "token_uri": os.environ[u'FIREBASE_TOKEN_URI'],
        "auth_provider_x509_cert_url": os.environ[u'FIREBASE_PROVIDER_CERT_URL'],
        "client_x509_cert_url": os.environ[u'FIREBASE_CLIENT_CERT_URL']
    }
    # Load Firebase credentials
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

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

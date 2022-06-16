# Heathcliff RSS Feed

Web scraper and RSS feed generator for the Heathcliff comic strip by George Gately.

Pulls the latest comic link using the Selenium Python Library, writes the important data to a simple SQLite file, then spits out an RSS feed. Runs entirely inside a docker stack with the `firefox` container acting as the WebDriver for Selenium.

## To-Do

- [ ] Write logic to push and pull `heathcliff.db` from some form of cloud storage. This way the SQLite file is not ephemeral and can be pulled on container creation and updates can be pushed every day. This will likely be setup to accept an AWS S3 Bucket.
- [ ] Write logic to check for more than just today's comic. For example, check the last 10 or 20 days to make sure the database didnt miss a day for some reason.
- [ ] Publish the RSS feed via HTTP using django or flask.



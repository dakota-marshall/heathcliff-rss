# Heathcliff RSS Feed

Web scraper and RSS feed generator for the Heathcliff comic strip by George Gately.

Pulls the latest comic link using the Selenium Python Library, writes the data to a document database (Firestore), then spits out an RSS feed. Runs entirely inside a docker stack with the `firefox` container acting as the WebDriver for Selenium.

## Deployment

To deploy this container, there are currently a few assumptions:
- There is a WebDriver container reachable at `http://firefox:4444` (This is on the todo to fix)
- This WebDriver container is using Firefox's geckodriver
- You will be using Firebase's Firestore Document Database for storing the post details

The following environment variables need to be configured for the container to function. These can be found from your service account private key in firebase:

```
FIREBASE_TYPE
FIREBASE_PROJECT_ID
FIREBASE_PRIV_KEY_ID
FIREBASE_PRIV_KEY
FIREBASE_CLIENT_EMAIL
FIREBASE_CLIENT_ID
FIREBASE_AUTH_URI
FIREBASE_TOKEN_URI
FIREBASE_PROVIDER_CERT_URL
FIREBASE_CLIENT_CERT_URL
```

## To-Do

- [x] Write logic to push and pull `heathcliff.db` from some form of cloud storage. This way the SQLite file is not ephemeral and can be pulled on container creation and updates can be pushed every day. This will likely be setup to accept an AWS S3 Bucket.
- [ ] Write logic to check for more than just today's comic. For example, check the last 10 or 20 days to make sure the database didnt miss a day for some reason.
- [ ] Read WebDriver URL from environment variable


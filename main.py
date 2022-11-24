import os
import datetime
import dotenv
from dotenv import load_dotenv
from time import sleep
import apprise

from oauth2client import client # Added
from oauth2client import tools # Added
from oauth2client.file import Storage # Added
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

# Set up Apprise, if enabled
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS")
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")

# Whether to use keep_alive.py
if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive import keep_alive
    keep_alive()
    
API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = "CLIENT_SECRET.json"

def apprise_init():
    if APPRISE_ALERTS:
        alerts = apprise.Apprise()
        # Add all services from .env
        for service in APPRISE_ALERTS:
            alerts.add(service)
        return alerts

def get_service():
    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()

def get_stats(start = datetime.datetime.now().strftime("%Y-%m-01"), end = datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate = start,
        endDate = end,
        metrics='views,estimatedMinutesWatched,estimatedRevenue',
    )
    # Retrieve the data from the response
    views = response['rows'][0][0]
    minutes = response['rows'][0][1]
    revenue = response['rows'][0][2]

    # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
    start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

    response = f'Views:\t{views:,}\nMinutes Watched:\t{minutes:,}\nEstimated Revenue:\t${revenue:,}'
    print(response)
    alerts.notify(title=f'YouTube Analytics Report ({start}\t-\t{end})', body=f'\n{response}\n\n...')

def main():
    while True:
        try:
            get_stats()
            get_stats('2021-10-01', '2022-11-01')
            get_stats('2016-01-01', '2022-11-24')
            print("Sleeping for 6 hours...")
            # sleep for 6 hours
            sleep(21600)
        except Exception as e:
            print(f'Received error: {e}')
            alerts.notify(title=f'YouTube Analytics Report Error', body=f'\n{e}\n\n...')

if __name__ == "__main__":
    if APPRISE_ALERTS:
        alerts = apprise_init()
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    main()

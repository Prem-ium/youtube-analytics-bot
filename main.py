import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from oauth2client import client # Added
from oauth2client import tools # Added
from oauth2client.file import Storage # Added
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import apprise
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS", None)

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = "CLIENT_SECRET.json"

# Methods
def apprise_init():
    if APPRISE_ALERTS:
        alerts = apprise.Apprise()
        for service in APPRISE_ALERTS:
            alerts.add(service)
        return alerts

def get_service(): # Modified
    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()
def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    youtubeAnalytics = get_service()
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate='2022-10-01',
        endDate='2022-11-01',
        metrics='estimatedRevenue',
        #dimensions='day',
        #sort='day'
    )
    print(response)
    

if __name__ == "__main__":
    main()
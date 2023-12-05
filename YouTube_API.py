# Github Repository: https://github.com/Prem-ium/youtube-analytics-bot

# BSD 3-Clause License
# 
# Copyright (c) 2022-present, Prem Patel
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os, datetime, traceback, calendar, requests, json, asyncio

from calendar                       import monthrange
from dotenv                         import load_dotenv

import discord
import google, google_auth_oauthlib, googleapiclient.errors

from oauth2client.client            import HttpAccessTokenRefreshError
from googleapiclient.discovery      import build, build_from_document
from oauth2client.file              import Storage
from discord.ext                    import commands
from oauth2client                   import client, tools
from google.oauth2.credentials      import Credentials

# Load the .env file & assign the variables
load_dotenv()

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]

DEV_MODE = (os.environ.get("DEV_MODE", "False").lower() == "true")

if DEV_MODE:
    print("- " * 25)
    print("Attention: Developer mode enabled.")
    print("The program will rely on the CLIENT_SECRET JSON Dict assigned to the proper .env variable.")
    print("It will not search for or use a CLIENT_SECRET.json file.")
    print("- " * 25)

    try:
        CLIENT_SECRETS = json.loads(os.environ.get("CLIENT_SECRET", None))['installed']
    except: raise Exception("CLIENT_SECRET is missing within .env file, please add it and try again.")

else:
    CLIENT_SECRETS = os.environ.get("CLIENT_PATH", "CLIENT_SECRET.json")
    
# Declare global scope
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

def get_service (API_SERVICE_NAME='youtubeAnalytics', API_VERSION='v2', SCOPES=SCOPES):
    global DEV_MODE, CLIENT_SECRETS

    # Build the service object if DEV_MODE is enabled, otherwise use the credentials.json file
    if DEV_MODE:
        try:
            credentials = Credentials.from_authorized_user_info(CLIENT_SECRETS)
            return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        except: print(f'Failed to build service:\n{traceback.format_exc()}')

    try:
        credential_path = os.path.join('./', 'credentials.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRETS, SCOPES)
            credentials = tools.run_flow(flow, store)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    except: print(f'Failed to run client flow service: \n{traceback.format_exc()}')
    
    try:
        credentials = Credentials.from_authorized_user_info(CLIENT_SECRETS)
        json_path = 'API_Service/Analytics-Service.json' if API_SERVICE_NAME == 'youtubeAnalytics' else 'API_Service/YouTube-Data-API.json'
        print(f'Building failed (This is expected behavior on replit.com), trying to build from document: {json_path}')
        with open(json_path) as f:
            service = json.load(f)
        return build_from_document(service, credentials = credentials)
    except Exception as e:
        print(f'Failed: Exhaused all get_service methods: \n{traceback.format_exc()}')
        raise

# Swap between dev mode and normal mode
async def dev_mode():
    global DEV_MODE, CLIENT_SECRETS
    DEV_MODE = not DEV_MODE
    
    if DEV_MODE:
        # Developer mode is enabled
        print("Developer mode is enabled. The program will rely on CLIENT_SECRET JSON Dict assigned to the proper .env variable.")
        print("Check .env.example for an example. Remember to add your refresh token in the JSON.\n")
        try:
            CLIENT_SECRETS = json.loads(os.environ.get("CLIENT_SECRET", "{}")).get("installed")
            if CLIENT_SECRETS is None:
                raise Exception("CLIENT_SECRET is missing within .env file. Please add it and try again.")
        except json.JSONDecodeError:
            raise Exception("CLIENT_SECRET in .env is not a valid JSON string.")
    else:
        CLIENT_SECRETS = os.environ.get("CLIENT_PATH", "CLIENT_SECRET.json")
        
def refresh_token (token=None):
    print(f'Refreshing Credentials Access Token...')
    global DEV_MODE
    if DEV_MODE:
        global CLIENT_SECRETS
        global YOUTUBE_ANALYTICS
        global YOUTUBE_DATA

        if token is not None:
            try:
                refresh_token = {"refresh_token": token}
                CLIENT_SECRETS.update(refresh_token)
                return f"Dev Mode: Successfully updated refresh token to {token}\nYou will need to update if the bot is restarted.\n"
            except Exception as e: return f"Ran into {e.__class__.__name__} Exception: {e}"

        data = {
            'client_id': CLIENT_SECRETS['client_id'],
            'client_secret': CLIENT_SECRETS['client_secret'],
            'refresh_token': CLIENT_SECRETS['refresh_token'],
            'grant_type': 'refresh_token'
        }
        response = requests.post('https://accounts.google.com/o/oauth2/token', data=data)
        if response.status_code == 200:
            response_json = response.json()
            CLIENT_SECRETS['access_token'] = response_json['access_token']
            CLIENT_SECRETS['expires_in'] = response_json['expires_in']

            # Calculate and update token expiry time
            now = datetime.datetime.now()
            CLIENT_SECRETS['token_expiry'] = (now + datetime.timedelta(seconds=response_json['expires_in'])).isoformat()

            message = f"{response.status_code}:\tSuccessfully refreshed token\n{datetime.datetime.now()}\n"
            YOUTUBE_ANALYTICS = get_service()
            YOUTUBE_DATA = get_service('youtube', 'v3', SCOPES)
        else:
            message = f"{response.status_code}:\tFalied to refresh token\t{datetime.datetime.now()}\n{response.text}"
    else:
        message = None
        with open('credentials.json') as f:
            cred = json.load(f)
            data = {
                'client_id': cred['client_id'],
                'client_secret': cred['client_secret'],
                'refresh_token': cred['refresh_token'],
                'grant_type': 'refresh_token'
            }

            response = requests.post('https://accounts.google.com/o/oauth2/token', data=data)
            if response.status_code == 200:
                response_json = response.json()
            
                # Update token_response with new access token and expiry time
                cred['token_response']['access_token'] = response_json['access_token']
                cred['token_response']['expires_in'] = response_json['expires_in']
                
                # Calculate and update token expiry time
                now = datetime.datetime.now()
                cred['token_expiry'] = (now + datetime.timedelta(seconds=response_json['expires_in'])).isoformat()
                message = f"{response.status_code}:\tSuccessfully refreshed token\n{datetime.datetime.now()}\n"
                # Save updated credentials to file
                with open('credentials.json', 'w') as f:
                    json.dump(cred, f)
            else:
                message = f"{response.status_code}:\tFalied to refresh token\t{datetime.datetime.now()}\n{response.text}"
    return message



# Refresh the token
async def refresh(return_embed=False, token=None):
    message = refresh_token(token)
    if return_embed:
        embed = discord.Embed(title=f"YouTube Analytics Bot Refresh", color=0x00ff00)
        embed.add_field(name="Status", value=message, inline=False)
        return embed
    else:
        return message
def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()

# Discord bot command methods.
async def get_stats (start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        # Query the YouTube Analytics API
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            ids='channel==MINE',
            startDate=start,
            endDate=end,
            metrics='views,estimatedMinutesWatched,subscribersGained,subscribersLost,estimatedRevenue,cpm,monetizedPlaybacks,playbackBasedCpm,adImpressions,likes,dislikes,averageViewDuration,shares,averageViewPercentage,subscribersGained,subscribersLost',
        )

        # Retrieve the data from the response
        views = response['rows'][0][0]
        minutes = response['rows'][0][1]
        subscribersGained = response['rows'][0][2] - response['rows'][0][3]
        revenue = response['rows'][0][4]
        cpm = response['rows'][0][5]
        monetizedPlaybacks = response['rows'][0][6]
        playbackCpm = response['rows'][0][7]
        adImpressions = response['rows'][0][8]
        likes = response['rows'][0][9]
        dislikes = response['rows'][0][10]
        averageViewDuration = response['rows'][0][11]
        shares = response['rows'][0][12]
        averageViewPercentage = response['rows'][0][13]
        subscribersGained = response['rows'][0][14]
        subscribersLost = response['rows'][0][15]
        netSubscribers = subscribersGained - subscribersLost

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        # create a Discord Embed object
        embed = discord.Embed(title=f"YouTube Analytics Report ({start} - {end})", color=0x00ff00)

        # add fields to the embed
        embed.add_field(name="Views", value=f"{round(views,2):,}", inline=True)
        embed.add_field(name="Ratings", value=f"{100*round(likes/(likes + dislikes),2):,}%", inline=True)
        embed.add_field(name="Minutes Watched", value=f"{round(minutes,2):,}", inline=True)
        embed.add_field(name="Average View Duration", value=f"{round(averageViewDuration,2):,}s ({round(averageViewPercentage,2):,}%)", inline=True)
        embed.add_field(name="Net Subscribers", value=f"{round(netSubscribers,2):,}", inline=True)
        embed.add_field(name="Shares", value=f"{round(shares,2):,}", inline=True)
        
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        embed.add_field(name="Estimated Revenue", value=f"${round(revenue,2):,}", inline=True)
        embed.add_field(name="CPM", value=f"${round(cpm,2):,}", inline=True)
        embed.add_field(name="Monetized Playbacks (±2.0%)", value=f"{round(monetizedPlaybacks,2):,}", inline=True)
        embed.add_field(name="Playback CPM", value=f"${round(playbackCpm,2):,}", inline=True)
        embed.add_field(name="Ad Impressions", value=f"{round(adImpressions,2):,}", inline=True)

        # Build the response string
        response_str = f'YouTube Analytics Report ({start}\t-\t{end})\n\n'
        response_str += f'Views:\t{round(views,2):,}\nRatings:\t{100*round(likes/(likes + dislikes),2):,}%\nMinutes Watched:\t{round(minutes,2):,}\nAverage View Duration:\t{round(averageViewDuration,2):,}s ({round(averageViewPercentage,2):,}%)\nNet Subscribers:\t{round(netSubscribers,2):,}\nShares:\t{round(shares,2):,}\n\n'
        response_str += f'Estimated Revenue:\t${round(revenue,2):,}\nCPM:\t${round(cpm,2):,}\nMonetized Playbacks (±2.0%):\t{round(monetizedPlaybacks,2):,}\nPlayback CPM:\t${round(playbackCpm,2):,}\nAd Impressions:\t{round(adImpressions,2):,}'
        print(response_str + '\nSending to Discord...')

        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"


async def top_revenue (results=10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        # Query the YouTube Analytics API
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            ids='channel==MINE',
            startDate=start,
            endDate=end,
            dimensions='video',
            metrics='estimatedRevenue',
            sort='-estimatedRevenue',
            maxResults=results,
        )

        # Retrieve video IDs and earnings from the response
        video_ids = []
        earnings = []
        for data in response['rows']:
            video_ids.append(data[0])
            earnings.append(data[1])

        # Query the YouTube Data API
        request = YOUTUBE_DATA.videos().list(
            part="snippet",
            id=','.join(video_ids)
        )
        response = request.execute()

        # Format the start and end dates
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        # create a Discord Embed object
        embed = discord.Embed(title=f"Top {results} Earning Videos ({start} - {end})", color=0x00ff00)

        total = 0
        for i in range(len(response['items'])):
            embed.add_field(name=f"{i + 1}) {response['items'][i]['snippet']['title']}:\t${round(earnings[i], 2):,}", value=f"------------------------------------------------------------------------------------", inline=False)
            total += earnings[i]
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"Top {results} Total Earnings", value=f"${round(total, 2):,}", inline=False)

        # Build the response string
        response_str = f'Top {results} Earning Videos ({start}\t-\t{end}):\n\n'
        total = 0
        for i in range(len(response['items'])):
            response_str += f'{i + 1}) {response["items"][i]["snippet"]["title"]} - ${round(earnings[i], 2):,}\n'
            total += earnings[i]
        response_str += f'\n\nTop {results} Total Earnings: ${round(total, 2):,}'
        print(response_str)

        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"


async def top_countries_by_revenue (results=10, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        # Query the YouTube Analytics API
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            dimensions='country',
            metrics='estimatedRevenue',
            sort='-estimatedRevenue',
            maxResults=results,
        )

        # Format the start and end dates
        startDate, endDate = (startDate[5:] if startDate[:4] == endDate[:4] else f'{startDate[5:]}-{startDate[:4]}').replace(
            '-', '/'), (endDate[5:] if startDate[:4] == endDate[:4] else f'{endDate[5:]}-{endDate[:4]}').replace('-', '/')

        # Build the response string
        return_str = f'Top {results} Countries by Revenue: ({startDate}\t-\t{endDate})\n'

        embed = discord.Embed(title=f"Top {results} Countries by Revenue: ({startDate} - {endDate})", color=0x00ff00)
        for row in response['rows']:
            embed.add_field(name=f"{row[0]}:\t\t${round(row[1],2):,}", value=f"${round(row[1],2):,}", inline=False)
            return_str += f'{row[0]}:\t\t${round(row[1],2):,}\n'
            print(row[0], row[1])
        
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        return embed, return_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"


async def get_ad_preformance (start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            ids='channel==MINE',
            startDate=start,
            endDate=end,
            dimensions='adType',
            metrics='grossRevenue,adImpressions,cpm',
            sort='-grossRevenue'
        )

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start_str = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/')
        end_str = (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        response_str = f'Ad Preformance ({start_str}\t-\t{end_str})\n\n'
        embed = discord.Embed(title=f"Ad Preformance ({start_str} - {end_str})", color=0x00ff00)
        # Parse the response into nice formatted string
        for row in response['rows']:
            embed.add_field(name=f"{row[0]}:\t\t${round(row[1],2):,}", value=f"Gross Revenue:\t${round(row[1],2):,}\tCPM:\t${round(row[3],2):,}\tImpressions:\t{round(row[2],2):,}", inline=False)
            response_str += f'Ad Type:\t{row[0]}\n\tGross Revenue:\t${round(row[1],2):,}\tCPM:\t${round(row[3],2):,}\tImpressions:\t{round(row[2],2):,}\n\n\n'

        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"

# More detailed geo data/report
async def get_detailed_georeport (results=5, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        # Get top preforming countries by revenue
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            dimensions='country',
            metrics='views,estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue,grossRevenue,adImpressions,cpm,playbackBasedCpm,monetizedPlaybacks',
            sort='-estimatedRevenue',
            maxResults=results,
        )

        # Parse the response using rows and columnHeaders
        response_str = f'Top {results} Countries by Revenue: ({startDate} - {endDate})\n\n'
        embed = discord.Embed(title=f"Top {results} Countries by Revenue: ({startDate} - {endDate})", color=0x00ff00)
        for row in response['rows']:
            response_str += f'{row[0]}:\n'
            for i in range(len(row)):
                if "country" in response["columnHeaders"][i]["name"]:
                    continue
                response_str += f'\t{response["columnHeaders"][i]["name"]}:\t{round(row[i],2):,}\n'
                embed.add_field(name=f"{response['columnHeaders'][i]['name']}:", value=f"{round(row[i],2):,}", inline=False)
            response_str += '\n'

        print(f'Data received:\t{response}\n\nReport Generated:\n{response_str}')
        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"

async def get_demographics (startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        # Get top preforming countries by revenue
        response = execute_api_request(
            YOUTUBE_ANALYTICS.reports().query,
            dimensions="ageGroup,gender",
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics="viewerPercentage",
            sort="-viewerPercentage",
        )
        startDate, endDate = (startDate[5:] if startDate[:4] == endDate[:4] else f'{startDate[5:]}-{startDate[:4]}').replace('-', '/'), (endDate[5:] if startDate[:4] == endDate[:4] else f'{endDate[5:]}-{endDate[:4]}').replace('-', '/')
        response_str = f'Gender Viewership Demographics ({startDate}\t-\t{endDate})\n\n'
        embed = discord.Embed(title=f"Gender Viewership Demographics ({startDate}\t-\t{endDate})", color=0x00ff00)

        # Parse the response into nice formatted string
        for row in response['rows']:
            if round(row[2],2) < 1: break
            row[0] = row[0].split('e')

            response_str += f'{round(row[2],2)}% Views come from {row[1]} with age of {row[0][1]}\n'
            embed.add_field(name=f"{round(row[2],2)}% Views come from {row[1]} with age of {row[0][1]}", value=f"{round(row[2],2)}%", inline=False)
        print(f'Demographics Report Generated & Sent:\n{response_str}')
        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"

async def get_shares (results = 5, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        request = YOUTUBE_ANALYTICS.reports().query(
            dimensions="sharingService",
            startDate=start,
            endDate=end,
            ids="channel==MINE",
            maxResults=results,
            metrics="shares",
            sort="-shares"
        ).execute()

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start_str, end_str = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        response_str = f'Top Sharing Services ({start_str}\t-\t{end_str})\n\n'
        embed = discord.Embed(title=f"Top Sharing Services ({start_str}\t-\t{end_str})", color=0x00ff00)
        # Parse the response into nice formatted string
        for row in request['rows']:
            response_str += f'{row[0].replace("_", " ")}:\t{row[1]:,}\n'
            embed.add_field(name=f'{row[0].replace("_", " ")}:', value=f"{row[1]:,}", inline=False)
        print(f'Shares Report Generated & Sent:\n{response_str}')
        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"

async def get_traffic_source (results=10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        request = YOUTUBE_ANALYTICS.reports().query(
            dimensions="insightTrafficSourceDetail",
            endDate=end,
            filters="insightTrafficSourceType==YT_SEARCH",
            ids="channel==MINE",
            maxResults=results,
            metrics="views",
            sort="-views",
            startDate=start
        ).execute()

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start_str, end_str = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        response_str = f'Top Search Traffic Terms ({start_str}\t-\t{end_str})\n\n'
        embed = discord.Embed(title=f"Top Search Traffic Terms ({start_str}\t-\t{end_str})", color=0x00ff00)
        # Parse the response into nice formatted string
        for row in request['rows']:
            response_str += f'{row[0].replace("_", " ")}:\t{row[1]:,}\n'
            embed.add_field(name=f'{row[0].replace("_", " ")}:', value=f"{row[1]:,}", inline=False)
        print(f'Traffic Report Generated:\n{response_str}')

        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"


async def get_operating_stats (results = 10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        request = YOUTUBE_ANALYTICS.reports().query(
            dimensions="operatingSystem",
            endDate=end,
            maxResults=results,
            ids="channel==MINE",
            metrics="views,estimatedMinutesWatched",
            sort="-views,estimatedMinutesWatched",
            startDate=start
        ).execute()
        start_str, end_str = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')
        response_str = f'Top Operating System ({start_str}\t-\t{end_str})\n'
        embed = discord.Embed(title=f"Top Operating System ({start_str}\t-\t{end_str})", color=0x00ff00)
        for row in request['rows']:
            response_str += f'\t{row[0]}:\n\t\tViews:\t\t{round(row[1], 2):,}\n\t\tEstimated Watchtime:\t\t{round(row[2],2):,}\n'
            embed.add_field(name=f'{row[0]}:', value=f"Views:\t\t{round(row[1], 2):,}\nEstimated Watchtime:\t\t{round(row[2],2):,}", inline=False)
        print(response_str)
        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"
    
async def get_playlist_stats (results = 5, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        request = YOUTUBE_ANALYTICS.reports().query(
            dimensions="playlist",
            endDate=end,
            filters="isCurated==1",
            ids="channel==MINE",
            maxResults=results,
            metrics="estimatedMinutesWatched,views,playlistStarts,averageTimeInPlaylist",
            sort="-views",
            startDate=start
        )
        response = request.execute()

        playlist_ids = ','.join([row[0] for row in response['rows']])
        playlist_ids = []
        views = []
        playlist_starts = []
        average_time_in_playlist = []
        estimated_minutes_watched = []
        for row in response['rows']:
            playlist_ids.append(row[0])
            views.append(row[1])
            playlist_starts.append(row[2])
            average_time_in_playlist.append(row[3])
            estimated_minutes_watched.append(row[4])

        request = YOUTUBE_DATA.playlists().list(
            part="snippet",
            id=playlist_ids
        )
        response = request.execute()
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')
        response_str = f'```YouTube Analytics Report ({start}\t-\t{end})\n\n'
        embed = discord.Embed(title=f"Top Operating System ({start}\t-\t{end})", color=0x00ff00)
        for row in response['items']:
            response_str += f"{row['snippet']['title']}:\nViews: {views[playlist_ids.index(row['id'])]}\nPlaylist Starts: {playlist_starts[playlist_ids.index(row['id'])]}\nAverage Time Spent in Playlist: {average_time_in_playlist[playlist_ids.index(row['id'])]}\nEstimated Minutes Watched: {estimated_minutes_watched[playlist_ids.index(row['id'])]}\n\n"
            embed.add_field(name=f'{row["snippet"]["title"]}:', value=f"Views: {views[playlist_ids.index(row['id'])]}\nPlaylist Starts: {playlist_starts[playlist_ids.index(row['id'])]}\nAverage Time Spent in Playlist: {average_time_in_playlist[playlist_ids.index(row['id'])]}\nEstimated Minutes Watched: {estimated_minutes_watched[playlist_ids.index(row['id'])]}", inline=False)
        response_str += '```'
        print('Playlist Report Generated:\n', response_str)
        return embed, response_str
    
    except HttpAccessTokenRefreshError:     return "The credentials have been revoked or expired, please re-run the application to re-authorize."
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, {traceback.format_exc()}"
    
YOUTUBE_ANALYTICS = get_service()
YOUTUBE_DATA = get_service("youtube", "v3", YOUTUBE_API_KEY)
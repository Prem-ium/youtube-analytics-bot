import os, datetime, traceback, calendar

from calendar import monthrange
from dotenv import load_dotenv
from time import sleep

import google
import google_auth_oauthlib
import googleapiclient.errors
import discord

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError, UserAccessTokenError, GoogleAuthError
from googleapiclient.discovery import build
from oauth2client.file import Storage
from discord.ext import commands, tasks
from oauth2client import client, tools

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

if not os.environ["DISCORD_TOKEN"]:
    raise Exception("DISCORD_TOKEN is missing within .env file, please add it and try again.")
elif not os.environ["YOUTUBE_API_KEY"]:
    raise Exception("This bot relies on YouTube Analytics AND Data API, please enable YouTube Data API.\nInsert the YouTube Data API key within YOUTUBE_API_KEY varibale in .env and try again.\n")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_CHANNEL = os.environ.get("DISCORD_CHANNEL", None)

if DISCORD_CHANNEL:
    DISCORD_CHANNEL = int(DISCORD_CHANNEL)

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]

# Whether to use keep_alive.py
if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive import keep_alive
    keep_alive()

CLIENT_SECRETS_FILE = "CLIENT_SECRET.json"

def get_service(API_SERVICE_NAME='youtubeAnalytics', API_VERSION='v2', SCOPES=SCOPES, CLIENT_SECRETS_FILE=CLIENT_SECRETS_FILE):
    credential_path = os.path.join('./', 'credentials.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()

async def update_dates(startDate, endDate):
    splitStartDate, splitEndDate = startDate.split('/'), endDate.split('/')

    # If the start and end dates are in the first month of the year & they are the same date
    if (splitStartDate[1] == '01' and (splitStartDate[0] == splitEndDate[0] and splitEndDate[1] in ['01', '02', '03'])):
        # Get the year from the start date, or use the current year
        year = startDate.split('/')[2] if (len(startDate.split('/')) > 2) else datetime.datetime.now().strftime("%Y")
        # If month is January, use the previous year
        year = str(int(year) - 1 if int(splitStartDate[0]) == 1 else year)
        # Use the full 4-digit year
        year = f'20{year}' if len(year) == 2 else year
        # Get the previous month
        previousMonth = int(splitStartDate[0]) - 1 if int(splitStartDate[0]) > 1 else 12
        # Get the last day of the previous month
        lastDay = monthrange(int(year), previousMonth)[1]
        # Set the start and end dates to the previous month
        startDate = datetime.datetime.strptime(f'{previousMonth}/01', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(f'{previousMonth}/{lastDay}', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
    # If the start or end date is missing the year
    elif len(startDate) != 5 or len(endDate) != 5:
        # Set the start and end dates to the full date including the year
        startDate = datetime.datetime.strptime(startDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(endDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
    else:
        # Get the current year
        currentYear = datetime.datetime.now().strftime("%Y")
        # If the start date is missing the year
        if len(startDate) == 5:
            # Set the start date to the full date including the year
            startDate = datetime.datetime.strptime(startDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
        # If the end date is missing the year
        if len(endDate) == 5:
            # Set the end date to the full date including the year
            endDate = datetime.datetime.strptime(endDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
    # Print a message indicating the updated dates
    print(f'Updating dates to {startDate} - {endDate}')
    return startDate, endDate

async def get_stats(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        youtubeAnalytics = get_service()

        # Query the YouTube Analytics API
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=start,
            endDate=end,
            metrics='views,estimatedMinutesWatched,subscribersGained,subscribersLost,estimatedRevenue,cpm,monetizedPlaybacks,playbackBasedCpm,adImpressions',
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

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        # Build the response string
        response_str = f'YouTube Analytics Report ({start}\t-\t{end})\n\n'
        response_str += f'Views:\t{round(views,2):,}\nMinutes Watched:\t{round(minutes,2):,}\nSubscribers Gained:\t{round(subscribersGained,2):,}\n\n'
        response_str += f'Estimated Revenue:\t${round(revenue,2):,}\nCPM:\t${round(cpm,2):,}\nMonetized Playbacks (??2.0%):\t{round(monetizedPlaybacks,2):,}\nPlayback CPM:\t${round(playbackCpm,2):,}\nAd Impressions:\t{round(adImpressions,2):,}'

        print(response_str + '\nSending to Discord...')
        return response_str
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."


async def top_revenue(results=10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        youtubeAnalytics = get_service()

        # Query the YouTube Analytics API
        response = execute_api_request(
            youtubeAnalytics.reports().query,
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

        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Query the YouTube Data API
        request = youtube.videos().list(
            part="snippet",
            id=','.join(video_ids)
        )
        response = request.execute()

        # Format the start and end dates
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        # Build the response string
        top_results = f'Top {results} Earning Videos ({start}\t-\t{end}):\n\n'
        total = 0
        for i in range(len(response['items'])):
            top_results += f'{i + 1}) {response["items"][i]["snippet"]["title"]} - ${round(earnings[i], 2):,}\n'
            total += earnings[i]
        top_results += f'\n\nTop {results} Total Earnings: ${round(total, 2):,}'
        print(top_results)

        return top_results
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."


async def top_countries_by_revenue(results=10, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        youtubeAnalytics = get_service()

        # Query the YouTube Analytics API
        response = execute_api_request(
            youtubeAnalytics.reports().query,
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
        for row in response['rows']:
            return_str += f'{row[0]}:\t\t${round(row[1],2):,}\n'
            print(row[0], row[1])

        return return_str
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."


async def get_ad_preformance(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        youtubeAnalytics = get_service()

        response = execute_api_request(
            youtubeAnalytics.reports().query,
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

        preformance = f'Ad Preformance ({start_str}\t-\t{end_str})\n\n'

        # Parse the response into nice formatted string
        for row in response['rows']:
            preformance += f'Ad Type:\t{row[0]}\n\tGross Revenue:\t${round(row[1],2):,}\tCPM:\t${round(row[3],2):,}\tImpressions:\t{round(row[2],2):,}\n\n\n'

        return preformance

    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."

# More detailed geo data/report
async def get_detailed_georeport(results=5, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        youtubeAnalytics = get_service()
        # Get top preforming countries by revenue
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            dimensions='country',
            metrics='views,estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue,grossRevenue,adImpressions,cpm,playbackBasedCpm,monetizedPlaybacks',
            sort='-estimatedRevenue',
            maxResults=results,
        )

        # Parse the response using rows and columnHeaders
        report = f'Top {results} Countries by Revenue: ({startDate} - {endDate})\n\n'
        for row in response['rows']:
            report += f'{row[0]}:\n'
            for i in range(len(row)):
                if "country" in response["columnHeaders"][i]["name"]:
                    continue
                report += f'\t{response["columnHeaders"][i]["name"]}:\t{round(row[i],2):,}\n'
                
                if len(report) > 1500:
                    return report

            report += '\n'

        print(f'Data received:\t{response}\n\nReport Generated:\n{report}')
        return report
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."

async def get_demographics(startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        youtubeAnalytics = get_service()
        # Get top preforming countries by revenue
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            dimensions="ageGroup,gender",
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics="viewerPercentage",
            sort="-viewerPercentage",
        )

               # Format the start and end dates
        startDate, endDate = (startDate[5:] if startDate[:4] == endDate[:4] else f'{startDate[5:]}-{startDate[:4]}').replace(
            '-', '/'), (endDate[5:] if startDate[:4] == endDate[:4] else f'{endDate[5:]}-{endDate[:4]}').replace('-', '/')
        demographics = f'Gender Viewership Demographics ({startDate}\t-\t{endDate})\n\n'

        # Parse the response into nice formatted string
        for row in response['rows']:
            if round(row[2],2) < 1: break
            # split string after index of 'e'
            row[0] = row[0].split('e')

            demographics += f'{round(row[2],2)}% Views come from {row[1]} with age of {row[0][1]}\n'
        print(f'Demographics Report Generated & Sent:\n{demographics}')
        return demographics

    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."

async def get_shares(results = 5, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    request = youtubeAnalytics.reports().query(
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

    shares = f'Top Sharing Services ({start_str}\t-\t{end_str})\n\n'
    # Parse the response into nice formatted string
    for row in request['rows']:
        shares += f'{row[0].replace("_", " ")}:\t{row[1]:,}\n'
    print(f'Shares Report Generated & Sent:\n{shares}')
    return shares

async def get_traffic_source(results=10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    request = youtubeAnalytics.reports().query(
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

    traffic = f'Top Search Traffic Terms ({start_str}\t-\t{end_str})\n\n'
    # Parse the response into nice formatted string
    for row in request['rows']:
        traffic += f'{row[0].replace("_", " ")}:\t{row[1]:,}\n'
    print(f'Traffic Report Generated:\n{traffic}')

    return traffic


async def get_operating_stats(results = 10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    request = youtubeAnalytics.reports().query(
        dimensions="operatingSystem",
        endDate=end,
        #filters="deviceType==MOBILE",
        maxResults=results,
        ids="channel==MINE",
        metrics="views,estimatedMinutesWatched",
        sort="-views",
        startDate=start
    ).execute()
    print(request)
    # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
    start_str, end_str = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace(
        '-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')
    os = f'Top Operating System ({start_str}\t-\t{end_str})\n'
    # {round(row[i],2):,}
    for row in request['rows']:
        os += f'\t{row[0]}:\n\t\tViews:\t\t{round(row[1], 2):,}\n\t\tEstimated Watchtime:\t\t{round(row[1],2):,}\n'
    return os

if __name__ == "__main__":
    # Set the intents for the bot
    discord_intents = discord.Intents.all()
    # Create the bot with the specified command prefix and intents
    bot = commands.Bot(command_prefix='!', intents=discord_intents)
    # Remove the default 'help' command
    bot.remove_command('help')

    # Bot event when bot is ready
    if DISCORD_CHANNEL:
        # Define the event handler
        @bot.event
        async def on_ready():
            # Get the specified channel
            channel = bot.get_channel(DISCORD_CHANNEL)
            # Send a message to the channel indicating that the bot is ready
            await channel.send('Analytics Bot is ready!')

    # Bot ping-pong command
    @bot.command(name='ping')
    async def ping(ctx):
        # Send a 'pong' message to the user
        await ctx.send('pong')
        # Print a message to the console indicating that the user got ponged
        print(
            f'\n{ctx.author.name} just got ponged!\t{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}\n')

    # Retrieve Analytic stats within specified date range, defaults to current month
    @bot.command(aliases=['stats', 'thisMonth'])
    async def analyze(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        # Update the start and end dates to be in the correct format
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            # Get the stats for the specified date range
            stats = await get_stats(startDate, endDate)        
            # Send the stats to the user
            await ctx.send(stats)
            # Print a message to the console indicating that the stats were sent
            print(f'\n{startDate} - {endDate} stats sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    # Lifetime stats
    @bot.command(aliases=['lifetime', 'alltime'])
    async def lifetime_method(ctx):
        try:
            stats = await get_stats('2005-02-14', datetime.datetime.now().strftime("%Y-%m-%d"))
            await ctx.send(stats)
            print('\nLifetime stats sent\n')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    @bot.command(aliases=['lastMonth'])
    async def lastmonth(ctx):
        # Get the last month's start and end dates
        startDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        endDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        startDate = startDate.replace(day=1)
        endDate = endDate.replace(day=calendar.monthrange(endDate.year, endDate.month)[1])
        try:
            stats = await get_stats(startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))
            # Send the stats to the user
            await ctx.send(stats)
            print(f'\nLast month ({startDate} - {endDate}) stats sent\n')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Retrieve top earning videos within specified date range between any month/year, defaults to current month
    @bot.command(aliases=['getMonth'])
    async def month(ctx, period=datetime.datetime.now().strftime("%m/%Y")):
        # Split the period into month and year
        period = period.split('/')
        month, year = period[0], period[1]
        # Add a '20' prefix to the year if it has only two digits
        year = f'20{year}' if len(year) == 2 else year
        # Get the last day of the month
        lastDate = monthrange(int(year), int(month))[1]
        # Get the start and end dates in the correct format
        startDate = datetime.datetime.strptime(
            f'{month}/01', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(
            f'{month}/{lastDate}', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        try:
            stats = await get_stats(startDate, endDate)
            # Send the stats to the user
            await ctx.send(stats)
            print(f'\nLast month ({startDate} - {endDate}) stats sent\n')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Retrieve top earning videos within specified date range, defaults to current month
    @bot.command(aliases=['topEarnings'])
    async def top(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            rev = await top_revenue(results, startDate, endDate)
            # Send the stats to the user
            await ctx.send(rev)
            print(f'\n{startDate} - {endDate} top {results} sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Top revenue by country
    @bot.command(aliases=['geo_revenue', 'geoRevenue'])
    async def detailed_georeport(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)        
        try:
            stats = await top_countries_by_revenue(results, startDate, endDate)
            # Send the stats to the user
            await ctx.send(stats)
            print(f'\nLast month ({startDate} - {endDate}) geo-revenue report sent\n')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Geo Report (views, revenue, cpm, etc)
    @bot.command(aliases=['geo_report', 'geoReport'])
    async def country(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=3):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_detailed_georeport(results, startDate, endDate)
            # Send the stats to the user
            await ctx.send(stats)
            print(f'\n{startDate} - {endDate} earnings by country sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Ad Type Preformance Data
    @bot.command(aliases=['adtype', 'adPreformance'])
    async def ad(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_ad_preformance(startDate, endDate)
            # Send the stats to the user
            await ctx.send(stats)
            print(f'\n{startDate} - {endDate} ad preformance sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Demographics Report
    @bot.command(aliases=['demographics', 'gender', 'age'])
    async def demo_graph(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            await ctx.send(await get_demographics(startDate, endDate))
            print(f'\n{startDate} - {endDate} demographics sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    # Shares Report
    @bot.command(aliases=['shares', 'shares_report', 'sharesReport'])
    async def share_rep(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=5):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            await ctx.send(await get_shares(results, startDate, endDate))
            print(f'\n{startDate} - {endDate} shares result sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    # Search Terms Report
    @bot.command(aliases=['search', 'search_terms', 'searchTerms'])
    async def search_rep(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            await ctx.send(await get_traffic_source(results, startDate, endDate))
            print(f'\n{startDate} - {endDate} search terms result sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    # Top Operating Systems
    @bot.command(aliases=['os', 'operating_systems', 'operatingSystems'])
    async def top_os(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            await ctx.send(await get_operating_stats(results, startDate, endDate))
            print(f'\n{startDate} - {endDate} operating systems result sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return
    # Send everything.
    @bot.command(aliases=['everything'])
    async def all(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            # Get statistics
            stats = await get_stats(startDate, endDate)
            
            # Get top revenue
            top_rev = await top_revenue(10, startDate, endDate)
            
            # Get top countries by revenue
            top_countries = await top_countries_by_revenue(10, startDate, endDate)
            
            # Get ad performance
            ad_performance = await get_ad_preformance(startDate, endDate)
            
            # Get detailed georeport
            georeport = await get_detailed_georeport(3, startDate, endDate)
            
            # Get demographics report
            demographics = await get_demographics(startDate, endDate)

            # Get shares report
            shares = await get_shares(5, startDate, endDate)

            # Get search terms report
            search_terms = await get_traffic_source(10, startDate, endDate)

            # Get top operating systems
            top_os = await get_operating_stats(10, startDate, endDate)

            # Send everything
            await ctx.send(stats + '\n\n.')
            await ctx.send(top_rev + '\n\n.')
            await ctx.send(top_countries + '\n\n.')
            await ctx.send(ad_performance + '\n\n.')
            await ctx.send(georeport + '\n\n.')
            await ctx.send(demographics + '\n\n.')
            await ctx.send(shares + '\n\n.')
            await ctx.send(search_terms + '\n\n.')
            await ctx.send(top_os + '\n\n.')
            print(f'\n{startDate} - {endDate} everything sent')
        except UserAccessTokenError:
            # If the user's access token is invalid, send a message to the user
            await ctx.send('Your access token (credentials.json) is invalid, please re-authenticate & reb-build the bot.')
            # Print a message to the console indicating that the user's access token is invalid
            print(f'\n{ctx.author.name}\'s access token is invalid')
            # Return from the function
            return

    # Help command
    @bot.command()
    async def help(ctx):
        available_commands = [
            "!stats [startDate] [endDate] - Return stats within time range. Defaults to current month\nExample: !stats 01/01 12/1\t,\t!stats 01/01/2021 01/31/2021\n\n",
            "!getMonth [month/year] - Return stats for a specific month.\nExample: !getMonth 01/21\t,\t!getMonth 10/2020\n",
            "!lifetime - Get lifetime stats - Get lifetime stats\n",
            "!topEarnings [startDate] [endDate] [# of countries to return (Default: 10)] - Return top specified highest revenue earning videos.\nExample: !topEarnings 01/01 12/1 5\n\n",
            "!geo_revenue [startDate] [endDate] [# of countries to return] - Top Specific (default 10) countries by revenue\nExample: !geo_revenue 01/01 12/1 5\n\n",
            "!geoReport [startDate] [endDate] [# of countries to return] - More detailed report of views, revenue, cpm, etc by country\nExample: !geoReport 01/01 12/1 5\n\n",
            "!adtype [startDate] [endDate] - Get highest preforming ad types within specified time range\nExample: !adtype 01/01 12/1\n\n",
            "!demographics [startDate] [endDate] - - Get demographics data (age and gender) of viewers\nExample: !demographics 01/01 12/1\n\n",
            "!shares [startDate] [endDate] [# of results to return (Default: 5)] - Return top specified highest shares videos.\nExample: !shares 01/01 12/1 5\n\n",
            "!search [startDate] [endDate] [# of results to return (Default: 10)] - Return top specified highest search terms (ranked by views).\nExample: !search 01/01 12/1 5\n\n",
            "!os [startDate] [endDate] [# of results to return (Default: 10)] - Return top operating systems watching your videos (ranked by views).\nExample: !os 01/01 12/1 5\n\n",
            "!everything [startDate] [endDate] - Return everything. Call every method and output all available data\nExample: !everything 01/01 12/1\n\n",
            "!restart - Restart the bot",
            "!help\n!ping"
        ]
        
        # Use the join method to concatenate all the elements in the list
        available_commands = "\n".join(available_commands)

        await ctx.send(f"Available commands:\n\n{available_commands}\n\n\n\"[brackets indicate optional values to pass in, if none are provided, default values will be used.]\"\nMost commands can be called without specifying a date range. If no date range is specified, usually current or last month will be used.")

    # Restart command
    @bot.command(name='restart')
    async def restart(ctx):
        print("Restarting...")
        print()
        await ctx.send("Restarting...")
        await bot.close()
        os._exit(0)

    # Run Discord bot
    bot.run(DISCORD_TOKEN)
    print('Discord bot is online...')

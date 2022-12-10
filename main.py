import os, datetime, traceback, calendar

from calendar import monthrange
from dotenv import load_dotenv
from time import sleep

import google
import google_auth_oauthlib
import googleapiclient.errors
import discord

from google_auth_oauthlib.flow import InstalledAppFlow
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

    if (splitStartDate[1] == '01' and splitEndDate[1] == '01') and startDate == endDate:
        year = startDate.split('/')[2] if (len(startDate.split('/')) > 2) else datetime.datetime.now().strftime("%Y")
        year = f'20{year}' if len(year) == 2 else year
        previousMonth = int(splitStartDate[0]) - 1 if int(splitStartDate[0]) > 1 else 12
        lastDay = monthrange(int(year), previousMonth)[1]

        # Assign the new dates to the variables & return them
        startDate = datetime.datetime.strptime(f'{previousMonth}/01', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(f'{previousMonth}/{lastDay}', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
    elif len(startDate) != 5 or len(endDate) != 5:
        startDate = datetime.datetime.strptime(startDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(endDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
    else:
        currentYear = datetime.datetime.now().strftime("%Y")
        if len(startDate) == 5:
            startDate = datetime.datetime.strptime(startDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
        if len(endDate) == 5:
            endDate = datetime.datetime.strptime(endDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
    print(f'Updating dates to {startDate} - {endDate}')
    return startDate, endDate


async def get_stats(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        youtubeAnalytics = get_service()
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=start,
            endDate=end,
            metrics='views,estimatedMinutesWatched,estimatedRevenue,playbackBasedCpm',
        )
        # Retrieve the data from the response
        views = response['rows'][0][0]
        minutes = response['rows'][0][1]
        revenue = response['rows'][0][2]
        cpm = response['rows'][0][3]

        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace(
            '-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        response = f'YouTube Analytics Report ({start}\t-\t{end})\n\nViews:\t{round(views,2):,}\nMinutes Watched:\t{round(minutes,2):,}\nEstimated Revenue:\t${round(revenue,2):,}\nPlayback CPM:\t${round(cpm,2):,}'
        print(response + '\nSending to Discord...')
        return response
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."


async def top_revenue(results=10, start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    try:
        youtubeAnalytics = get_service()
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
        video_ids = []
        earnings = []
        for data in response['rows']:
            video_ids.append(data[0])
            earnings.append(data[1])

        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        request = youtube.videos().list(
            part="snippet",
            id=','.join(video_ids)
        )
        response = request.execute()
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        top_results = f'Top {results} Earning Videos ({start}\t-\t{end})\n:\n\n'
        for i in range(len(response['items'])):
            top_results += f'{response["items"][i]["snippet"]["title"]} - ${round(earnings[i], 2):,}\n'
        print(top_results)

        return top_results
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."

async def top_countries_by_revenue(results=10, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    try:
        youtubeAnalytics = get_service()
        # Get top preforming countries by revenue
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
        startDate, endDate = (startDate[5:] if startDate[:4] == endDate[:4] else f'{startDate[5:]}-{startDate[:4]}').replace(
            '-', '/'), (endDate[5:] if startDate[:4] == endDate[:4] else f'{endDate[5:]}-{endDate[:4]}').replace('-', '/')

        returnString = f'Top {results} Countries by Revenue: ({startDate}\t-\t{endDate})\n'
        for row in response['rows']:
            returnString += f'{row[0]}:\t\t${round(row[1],2):,}\n'
            print(row[0], row[1])

        return returnString
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
            sort='adType'
        )
        # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
        start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace(
            '-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

        preformance = f'Ad Preformance ({start}\t-\t{end})\n\n'
        # Parse the response into nice formatted string
        for row in response['rows']:
            preformance += f'{row[0]}:\n\t\t\t\t\t\t\tGross Revenue:\t${round(row[1],2):,}\tImpressions:\t{round(row[2],2):,}\tCPM:\t${round(row[3],2):,}\n'
            print(row[0], row[1], row[2], row[3])
        return preformance
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into {e.__class__.__name__} exception, please check the logs."

# More detailed geo data/report
async def get_detailed_georeport(results=5, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
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
    report = f'Top {results} Countries by Revenue: ({startDate} - {endDate})\n\n'
    # Parse the response using rows and columnHeaders
    for row in response['rows']:
        for i in range(len(row)):
            try:    report += f'{response["columnHeaders"][i]["name"]}:{row[i]:,}\n'
            except: report += f'{response["columnHeaders"][i]["name"]}:{row[i]}\n'
            if (len(report) > 1500): return report
        report += '\n'
    print(f'Data received:\t{response}\n\nReport Generated:\n{report}')
    return report

if __name__ == "__main__":
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.remove_command('help')

    # Bot event when bot is ready
    if DISCORD_CHANNEL:
        @bot.event
        async def on_ready():
            channel = bot.get_channel(DISCORD_CHANNEL)
            await channel.send('Analytics Bot is ready!')

    # Bot ping-pong
    @bot.command(name='ping')
    async def ping(ctx):
        await ctx.send('pong')
        print(
            f'\n{ctx.author.name} just got ponged!\t{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}\n')

    # Retrieve Analytic stats within specified date range, defaults to current month
    @bot.command(aliases=['stats', 'thisMonth'])
    async def analyze(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await get_stats(startDate, endDate))
        print(f'\n{startDate} - {endDate} stats sent')

    # Retrieve top earning videos within specified date range, defaults to current month
    @bot.command(aliases=['lastMonth'])
    async def lastmonth(ctx):
        startDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        endDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        startDate = startDate.replace(day=1)
        endDate = endDate.replace(
            day=calendar.monthrange(endDate.year, endDate.month)[1])
        await ctx.send(await get_stats(startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d")))
        print(f'\nLast month ({startDate} - {endDate}) stats sent\n')

    # Retrieve top earning videos within specified date range between any month/year, defaults to current month
    @bot.command(aliases=['getMonth'])
    async def month(ctx, period=datetime.datetime.now().strftime("%m/%Y")):
        period = period.split('/')
        month, year = period[0], period[1]
        year = f'20{year}' if len(year) == 2 else year
        lastDate = monthrange(int(year), int(month))[1]
        startDate = datetime.datetime.strptime(
            f'{month}/01', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(
            f'{month}/{lastDate}', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        await ctx.send(await get_stats(startDate, endDate))
        print(f'\n{period} stats sent\n')

    # Retrieve top earning videos within specified date range, defaults to current month
    @bot.command(aliases=['topEarnings'])
    async def top(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await top_revenue(results, startDate, endDate))
        print(f'\n{startDate} - {endDate} top {results} sent')

    # Top revenue by country
    @bot.command(aliases=['geo_revenue', 'geoRevenue'])
    async def detailed_georeport(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await top_countries_by_revenue(results, startDate, endDate))
        print(f'\n{startDate} - {endDate} earnings by country sent')

    # Geo Report (views, revenue, cpm, etc)
    @bot.command(aliases=['geo_report', 'geoReport'])
    async def country(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=3):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await get_detailed_georeport(results, startDate, endDate))
        print(f'\n{startDate} - {endDate} earnings by country sent')

    # Ad Type Preformance Data
    @bot.command(aliases=['adtype', 'adPreformance'])
    async def ad(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await get_ad_preformance(startDate, endDate))
        print(f'\n{startDate} - {endDate} ad preformance sent')

    # Lifetime stats
    @bot.command(aliases=['lifetime', 'alltime'])
    async def lifetime_method(ctx):
        await ctx.send(await get_stats('2005-02-14', datetime.datetime.now().strftime("%Y-%m-%d")))
        print('\nLifetime stats sent\n')

    # Send everything.
    @bot.command(aliases=['everything'])
    async def all(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        await ctx.send(await get_stats(startDate, endDate) + '\n\n.')
        await ctx.send(await top_revenue(10, startDate, endDate) + '\n\n.')
        await ctx.send(await top_countries_by_revenue(10, startDate, endDate) + '\n\n.')
        await ctx.send(await get_ad_preformance(startDate, endDate) + '\n\n.')

        print(f'\n{startDate} - {endDate} everything sent')
    # Help command

    @bot.command()
    async def help(ctx):
        await ctx.send('Available commands:')
        await ctx.send('!stats [startDate] [endDate]- Return stats within time range. Defaults to current month\nExample: !stats 01/01 12/1 \t!stats 01/01/2021 01/31/2021')
        await ctx.send('!getMonth [month/year]- Return stats for a specific month.\nExample: !getMonth 01/21')
        await ctx.send('!topEarnings [startDate] [endDate] [# of countries to return (Default: 10)]- Return top specified highest revenue earning videos.')
        await ctx.send('!geo_revenue [startDate] [endDate] [# of countries to return]- Top Specific (default 10) countries by revenue')
        await ctx.send('!geoReport [startDate] [endDate] [# of countries to return]- More detailed report of views, revenue, cpm, etc by country')
        await ctx.send('!adtype [startDate] [endDate] - Get highest preforming ad types within specified time range')
        await ctx.send('!lifetime - Get lifetime stats')
        await ctx.send('!everything [startDate] [endDate]- Return everything. Call every method and output all available data')
        await ctx.send('!restart - Restart the bot')
        await ctx.send('!help\n!ping')

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

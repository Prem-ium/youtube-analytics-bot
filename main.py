import os
import datetime
import traceback
from dotenv import load_dotenv
from time import sleep
import discord
from discord.ext import commands, tasks
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.discovery import build
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
import google
import google_auth_oauthlib
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]


DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)
DISCORD_CHANNEL = os.environ.get("DISCORD_CHANNEL", None)

if DISCORD_CHANNEL:
    DISCORD_CHANNEL = int(DISCORD_CHANNEL)
if DISCORD_TOKEN is None:
    print("Discord token is not set in .env file!\nUnless you don't want to use Discord, in which case you can ignore this message.")
elif DISCORD_CHANNEL is None:
    print("Discord channel is not set in .env file!\nUnless you don't want to use Discord, in which case you can ignore this message.")

# Whether to use keep_alive.py
if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive import keep_alive
    keep_alive()

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = "CLIENT_SECRET.json"


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


async def get_stats(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
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

    response = f'YouTube Analytics Report ({start}\t-\t{end})\n\nViews:\t{views:,}\nMinutes Watched:\t{minutes:,}\nEstimated Revenue:\t${revenue:,}\nPlayback CPM:\t${cpm:,}'
    print(response)

    return response


async def top_ten_earnings(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start,
        endDate=end,
        dimensions='video',
        metrics='estimatedRevenue',
        sort='-estimatedRevenue',
        maxResults=10,
    )
    video_ids = []
    earnings = []
    for data in response['rows']:
        video_ids.append(data[0])
        earnings.append(data[1])

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=os.environ.get('YOUTUBE_API_KEY'))

    request = youtube.videos().list(
        part="snippet",
        id=','.join(video_ids)
    )
    response = request.execute()
    start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace(
        '-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

    top_ten = f'Top 10 Earning Videos {start} - {end}:\n\n'
    for i in range(len(response['items'])):
        top_ten += f'{response["items"][i]["snippet"]["title"]} - ${earnings[i]}\n'
    print(top_ten)

    return top_ten


async def update_dates(startDate, endDate):
    if len(startDate) != 5 or len(endDate) != 5:
        startDate = datetime.datetime.strptime(
            startDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(
            endDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
    else:
        currentYear = datetime.datetime.now().strftime("%Y")
        if len(startDate) == 5:
            startDate = datetime.datetime.strptime(
                startDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
        if len(endDate) == 5:
            endDate = datetime.datetime.strptime(
                endDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
    return startDate, endDate


async def earnings_by_country(startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
    youtubeAnalytics = get_service()
    # Get top preforming countries by revenue
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=startDate,
        endDate=endDate,
        dimensions='country',
        metrics='grossRevenue',
        sort='-grossRevenue',
        maxResults=10,
    )
    startDate, endDate = (startDate[5:] if startDate[:4] == endDate[:4] else f'{startDate[5:]}-{startDate[:4]}').replace(
        '-', '/'), (endDate[5:] if startDate[:4] == endDate[:4] else f'{endDate[5:]}-{endDate[:4]}').replace('-', '/')

    returnString = f'Top 10 Countries by Revenue: ({startDate}\t-\t{endDate})\n'
    for row in response['rows']:
        returnString += f'{row[0]}: ${row[1]}\n'
        print(row[0], row[1])

    return returnString


async def get_ad_preformance(start=datetime.datetime.now().strftime("%Y-%m-01"), end=datetime.datetime.now().strftime("%Y-%m-%d")):
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
    # Turn response into a table
    table = []
    for row in response['rows']:
        table.append(row)
    # Get the total revenue
    revenue = 0
    for row in table:
        revenue += float(row[1])
    # Get the total impressions
    impressions = 0
    for row in table:
        impressions += float(row[2])
    # Get the total CPM
    cpm = 0
    for row in table:
        cpm += float(row[3])

    # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
    start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace(
        '-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')
    # Format the table
    table = f'Ad Type Preformance for ({start} - {end})\n{"_"*20}{"_"*20}{"_"*20}{"_"*20}\n{"Ad Type":<20}\t\t{"Revenue":<20}{"Impressions":<20}{"CPM":<20}\n{"_"*20}{"_"*20}{"_"*20}{"_"*20}\n'
    for row in response['rows']:
        table += f'{row[0]:<20}\t\t{row[1]:<20}{row[2]:<20}{row[3]:<20}{"_"*20}{"_"*20}{"_"*20}{"_"*20}\n'
    table += f'{"Total":<20}\t\t{round(revenue, 2):<20}{impressions:<20}{cpm:<20}\n{"_"*20}{"_"*20}{"_"*20}{"_"*20}\n'

    print(table + 'Table sent.')

    return table.replace('_', '-')


if __name__ == "__main__":
    if DISCORD_TOKEN or DISCORD_CHANNEL:
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
            print('Someone just got ponged!')
            await ctx.send('pong')

        @bot.command(aliases=['lifetime, alltime'])
        async def lifetime(ctx):
            print()
            # Get Lifetime stats from the get_stats function, and send it to the channel
            await ctx.send(await get_stats('2005-02-14', datetime.datetime.now().strftime("%Y-%m-%d")))
            print('\nLifetime stats sent\n')

        @bot.command(aliases=['monthly'])
        async def month(ctx):
            print()
            # Get Monthly stats from the get_stats function, and send it to the channel
            await ctx.send(await get_stats())
            print('\nMonthly stats sent\n')

        @bot.command(aliases=['stats'])
        async def analyze(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
            startDate, endDate = await update_dates(startDate, endDate)
            await ctx.send(await get_stats(startDate, endDate))
            print(f'\n{startDate} - {endDate} stats sent')

        @bot.command(aliases=['top10'])
        async def top(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
            startDate, endDate = await update_dates(startDate, endDate)
            await ctx.send(await top_ten_earnings(startDate, endDate))
            print(f'\n{startDate} - {endDate} top 10 sent')

        @bot.command(aliases=['everything'])
        async def all(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
            startDate, endDate = await update_dates(startDate, endDate)
            await ctx.send(await get_stats(startDate, endDate))
            await ctx.send(await top_ten_earnings(startDate, endDate))
            await ctx.send(await earnings_by_country(startDate, endDate))
            await ctx.send(await get_ad_preformance(startDate, endDate))

            print(f'\n{startDate} - {endDate} everything sent')

        @bot.command(aliases=['bycountry'])
        async def country(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
            startDate, endDate = await update_dates(startDate, endDate)
            await ctx.send(await earnings_by_country(startDate, endDate))
            print(f'\n{startDate} - {endDate} earnings by country sent')

        @bot.command(aliases=['adpreformance'])
        async def ad(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
            startDate, endDate = await update_dates(startDate, endDate)
            await ctx.send(await get_ad_preformance(startDate, endDate))
            print(f'\n{startDate} - {endDate} ad preformance sent')

        # Help command
        @bot.command()
        async def help(ctx):
            await ctx.send('Available commands:')
            await ctx.send('!ping\n!lifetime\n!stats [start date] [end date]\n!monthly\n!top10 [start date] [end date]\n!everything [start date] [end date]\n!adpreformance [start date] [end date]\nbycountry [start date] [end date]\n!restart')
            await ctx.send('!help')

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

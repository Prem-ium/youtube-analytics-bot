import os
import datetime
import traceback
import threading
from dotenv import load_dotenv
from time import sleep
import apprise
import discord
from discord.ext import commands, tasks
from oauth2client import client 
from oauth2client import tools 
from oauth2client.file import Storage 
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

# Set up Apprise, if enabled
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS")
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")


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

async def get_stats(start = datetime.datetime.now().strftime("%Y-%m-01"), end = datetime.datetime.now().strftime("%Y-%m-%d")):
    youtubeAnalytics = get_service()
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate = start,
        endDate = end,
        metrics='views,estimatedMinutesWatched,estimatedRevenue,playbackBasedCpm',
    )
    # Retrieve the data from the response
    views = response['rows'][0][0]
    minutes = response['rows'][0][1]
    revenue = response['rows'][0][2]
    cpm = response['rows'][0][3]

    # Terminary operator to check if start/end year share a year, and strip/remove if that's the case
    start, end = (start[5:] if start[:4] == end[:4] else f'{start[5:]}-{start[:4]}').replace('-', '/'), (end[5:] if start[:4] == end[:4] else f'{end[5:]}-{end[:4]}').replace('-', '/')

    response = f'YouTube Analytics Report ({start}\t-\t{end})\n\nViews:\t{views:,}\nMinutes Watched:\t{minutes:,}\nEstimated Revenue:\t${revenue:,}\nPlayback CPM:\t${cpm:,}'
    print(response)
    #alerts.notify(title=f'YouTube Analytics Report ({start}\t-\t{end})', body=f'\n{response}\n\n...')
    return response

# Dead code, but I'm keeping it here for now. 
def main():
    while True:
        try:
            # Get Monthly Stats
            get_stats()
            print("Sleeping for 6 hours...")
            # sleep for 6 hours
            sleep(21600)
        except Exception as e:
            print(traceback.format_exc())
            alerts.notify(title=f'YouTube Analytics Report Error', body=f'\n{traceback.format_exc()}\n\n...')

if __name__ == "__main__":
    if APPRISE_ALERTS:
        alerts = apprise_init()
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

        @bot.command(aliases=['lifetime,alltime'])
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
        async def analyze(ctx, startDate, endDate):
            if len(startDate) != 5 or len(endDate) != 5:
                startDate = datetime.datetime.strptime(startDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
                endDate = datetime.datetime.strptime(endDate, '%m/%d/%y').strftime('%Y/%m/%d').replace('/', '-')
            else:
                currentYear = datetime.datetime.now().strftime("%Y")
                if len(startDate) == 5:
                    startDate = datetime.datetime.strptime(startDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
                if len(endDate) == 5:
                    endDate = datetime.datetime.strptime(endDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')

            await ctx.send(await get_stats(startDate, endDate))
            print(f'\n{startDate} - {endDate} stats sent')

        # At 10 AM or 8:30 PM everyday, send the monthly stats to the channel
        #@tasks.loop(hours=24)
        #async def called_once_a_day():
        #    message_channel = bot.get_channel(DISCORD_CHANNEL)
        #    await message_channel.send(await get_stats())
#
        #@called_once_a_day.before_loop
        #async def before():
        #    await bot.wait_until_ready()
        #    print("Finished waiting")

        
        # Help command
        @bot.command()
        async def help(ctx):
            await ctx.send('Available commands:')
            await ctx.send('!ping\n!lifetime\n!stats [start date] [end date]\n!monthly')
            await ctx.send('!restart')
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
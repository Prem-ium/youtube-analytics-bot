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

import os, datetime, traceback, calendar, asyncio
from calendar                       import monthrange
from dotenv                         import load_dotenv
import discord
from discord.ext                    import commands

from YouTube_API                    import *

# Load the .env file & assign the variables
load_dotenv()

if not os.environ["DISCORD_TOKEN"]:
    raise Exception("ERROR: `DISCORD_TOKEN` is missing in .env, please add it and restart.")
elif not os.environ["YOUTUBE_API_KEY"]:
    raise Exception("ERROR: `YOUTUBE_API_KEY` is missing in .env, please add it and restart.")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_CHANNEL = os.environ.get("DISCORD_CHANNEL", None)

if DISCORD_CHANNEL:
    DISCORD_CHANNEL = int(DISCORD_CHANNEL)

if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive                 import keep_alive
    keep_alive()

# Change dates to API format
async def update_dates (startDate, endDate):
    splitStartDate, splitEndDate = startDate.split('/'), endDate.split('/')

    # If the start and end dates are in the first month of the year & they are the same date
    if (splitStartDate[1] == '01' and (splitStartDate[0] == splitEndDate[0] and splitEndDate[1] in ['01', '02', '03'])):
        year = startDate.split('/')[2] if (len(startDate.split('/')) > 2) else datetime.datetime.now().strftime("%Y")
        year = str(int(year) - 1 if int(splitStartDate[0]) == 1 else year)
        year = f'20{year}' if len(year) == 2 else year

        previousMonth = int(splitStartDate[0]) - 1 if int(splitStartDate[0]) > 1 else 12
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
        currentYear = datetime.datetime.now().strftime("%Y")
        if len(startDate) == 5:
            startDate = datetime.datetime.strptime(startDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
        if len(endDate) == 5:
            endDate = datetime.datetime.strptime(endDate, '%m/%d').strftime(f'{currentYear}/%m/%d').replace('/', '-')
    return startDate, endDate

if __name__ == "__main__":
    # Refresh Token & Retrieve Channel ID at Launch 
    try: refresh_token()
    except FileNotFoundError as e: print(f'{e.__class__.__name__, e}{get_service()}')

    try:    CHANNEL_ID = YOUTUBE_DATA.channels().list(part="id",mine=True).execute()['items'][0]['id']
    except: print(traceback.format_exc())

    
    # View class for Discord bot, handles all button interactions
    class SimpleView(discord.ui.View):     
        startDate: datetime = datetime.datetime.now().strftime("%Y-%m-01")
        endDate: datetime = datetime.datetime.now().strftime("%Y-%m-%d")

        def __init__(self, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), timeout=None):
            super().__init__(timeout=timeout)
            async def initialize_dates():
                self.startDate, self.endDate = await update_dates(startDate, endDate)
            
            asyncio.ensure_future(initialize_dates())
        
        ##TODO: Add a way to resend buttons without making bot edit the message & destroy old stats
        async def update_buttons(self, interaction: discord.Interaction, embed: discord.Embed, response_str: str):
            await interaction.response.edit_message(content=response_str, embed=embed, view=self)

        @discord.ui.button(label='Analytics', style=discord.ButtonStyle.blurple)
        async def channel_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_stats(start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)

        @discord.ui.button(label="Top Revenue Videos", style=discord.ButtonStyle.blurple)
        async def top_earners(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await top_revenue(results=10, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)

        @discord.ui.button(label="Search Keyword Terms", style=discord.ButtonStyle.blurple)
        async def search_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_traffic_source(results=10, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)

        @discord.ui.button(label='Playlist Stats', style=discord.ButtonStyle.blurple)
        async def playlist_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_playlist_stats(results=5, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)
        
        @discord.ui.button(label='Geographic', style=discord.ButtonStyle.blurple)
        async def geo_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_detailed_georeport(results=5, startDate=self.startDate, endDate=self.endDate)
            await self.update_buttons(interaction, embed, response_str)

            embed, response_str = await top_countries_by_revenue(results=5, start=self.startDate, end=self.endDate)
            await interaction.response.edit_message(content=response_str, embed=embed, view=self)

        @discord.ui.button(label='OS Stats', style=discord.ButtonStyle.blurple)
        async def os_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_operating_stats(results=5, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)
        
        @discord.ui.button(label='Traffic Source', style=discord.ButtonStyle.blurple)
        async def traffic_source(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_traffic_source(results=5, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)
        
        @discord.ui.button(label='Shares', style=discord.ButtonStyle.blurple)
        async def shares(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await get_shares(results=5, start=self.startDate, end=self.endDate)
            await self.update_buttons(interaction, embed, response_str)
        
        @discord.ui.button(label='Top Earning Countries', style=discord.ButtonStyle.blurple)
        async def highest_earning_countries(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed, response_str = await top_countries_by_revenue(results=5, startDate=self.startDate, endDate=self.endDate)
            await self.update_buttons(interaction, embed, response_str)

        @discord.ui.button(label='Refresh Token', style=discord.ButtonStyle.success)
        async def token_ref(self, interaction: discord.Interaction, button: discord.ui.Button):
            status = await refresh(return_embed=False)
            print(status)
            await interaction.response.send_message(status)

        @discord.ui.button(label='Ping!', style=discord.ButtonStyle.grey)
        async def got_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message('Pong!')


    discord_intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=discord_intents)
    bot.remove_command('help')

    if DISCORD_CHANNEL:
        @bot.event
        async def on_ready():
            channel = bot.get_channel(DISCORD_CHANNEL)

            await channel.send(embed=discord.Embed(
                title="YouTube Analytics Bot Online",
                description="The bot is ready to provide YouTube analytics at your command!",
                color=discord.Color.green()
            ))
            await channel.send(view=SimpleView())

    # Help command
    @bot.command()
    async def help(ctx):
        available_commands = [
            {"command": "!button",      "parameters": "[startDate] [endDate]",                  "description": "Opens a view shortcut for all available commands",              "example": "!button -- !button 01/01 12/01\n"},
            {"command": "!stats",       "parameters": "[startDate] [endDate]",                  "description": "Return stats within a time range (defaults to current month)",  "example": "!stats 01/01 12/01 -- !stats 01/01/2021 01/31/2021\n"},
            {"command": "!getMonth",    "parameters": "[month/year]",                           "description": "Return stats for a specific month",                             "example": "!getMonth 01/21 -- !getMonth 10/2020\n"},
            {"command": "!lifetime",    "parameters": "None",                                   "description": "Get lifetime stats",                                            "example": "!lifetime\n"},
            {"command": "!topEarnings", "parameters": "[startDate] [endDate] [# of countries]", "description": "Return top revenue-earning videos",                             "example": "!topEarnings 01/01 12/1 5\n"},
            {"command": "!geo_revenue", "parameters": "[startDate] [endDate] [# of countries]", "description": "Top countries by revenue",                                      "example": "!geo_revenue 01/01 12/1 5\n"},
            {"command": "!geoReport",   "parameters": "[startDate] [endDate] [# of countries]", "description": "More detailed revenue report by country",                       "example": "!geoReport 01/01 12/1 5\n"},
            {"command": "!adtype",      "parameters": "[startDate] [endDate]",                  "description": "Get highest performing ad types",                               "example": "!adtype 01/01 12/1\n"},
            {"command": "!demographics","parameters": "[startDate] [endDate]",                  "description": "Get viewer demographics data (age and gender)",                 "example": "!demographics 01/01 12/1\n"},
            {"command": "!shares",      "parameters": "[startDate] [endDate] [# of results]",   "description": "Return top videos by shares",                                   "example": "!shares 01/01 12/1 5\n"},
            {"command": "!search",      "parameters": "[startDate] [endDate] [# of results]",   "description": "Return top search terms by views",                              "example": "!search 01/01 12/1 5\n"},
            {"command": "!os",          "parameters": "[startDate] [endDate] [# of results]",   "description": "Return top operating systems by views",                         "example": "!os 01/01 12/1 5\n"},
            {"command": "!playlist",    "parameters": "[startDate] [endDate] [# of results]",   "description": "Return playlist stats",                                         "example": "!playlist 01/01 12/1\n"},
            {"command": "!everything",  "parameters": "[startDate] [endDate]",                  "description": "Return all available data",                                     "example": "!everything 01/01 12/1\n\n"},
            {"command": "!refresh",     "parameters": "None",                                   "description": "Refresh the API token",                                         "example": "!refresh"},
            {"command": "!switch",      "parameters": "None",                                   "description": "Toggle between dev and user mode (temporary)",                  "example": "!switch"},
            {"command": "!restart",     "parameters": "None",                                   "description": "Restart the bot",                                               "example": "!restart"},
            {"command": "!help",        "parameters": "None",                                   "description": "Show this help message",                                        "example": "!help"},
            {"command": "!ping",        "parameters": "None",                                   "description": "Check bot latency",                                             "example": "!ping"},
        ]
        current_field = "Parameters are optional, most commands have default dates, denoted by [].\n\n"

        for cmd_info in available_commands:
            field_content = f"**Command:** {cmd_info['command']}\n"
            field_content +=f"**Parameters:** {cmd_info['parameters']}\n" if cmd_info['parameters'] != "None" else ""
            field_content += f"**Description:** {cmd_info['description']}\n"
            field_content+=f"**Example:** {cmd_info['example']}\n\n" if cmd_info['example'] != cmd_info["command"] else "\n"

            current_field += field_content

        embed = discord.Embed(title="Help: Available Commands", color=0x00ff00)
        embed.description = current_field
        embed.set_footer(text="Bot developed by Prem-ium.\nhttps://github.com/Prem-ium/youtube-analytics-bot\n")
        await ctx.send(embed=embed)


    # Button command, opens a View with supported commands
    @bot.command()
    async def button(ctx, startDate, endDate):
        view = SimpleView(startDate, endDate, timeout=None)
        await ctx.send(view=view)


    # Retrieve Analytic stats within specified date range, defaults to current month
    @bot.command(aliases=['stats', 'thisMonth', 'this_month'])
    async def analyze(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        # Update the start and end dates to be in the correct format
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            # Get the stats for the specified date range
            stats = await get_stats(startDate, endDate)        
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            
            # Print a message to the console indicating that the stats were sent
            print(f'\n{startDate} - {endDate} stats sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Lifetime stats
    @bot.command(aliases=['lifetime', 'alltime', 'allTime'])
    async def lifetime_method(ctx):
        try:
            stats = await get_stats('2005-02-14', datetime.datetime.now().strftime("%Y-%m-%d"))
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Last month's stats
    @bot.command(aliases=['lastMonth'])
    async def lastmonthct(ctx):
        # Get the last month's start and end dates
        startDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        endDate = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        startDate = startDate.replace(day=1)
        endDate = endDate.replace(day=calendar.monthrange(endDate.year, endDate.month)[1])
        try:
            stats = await get_stats(startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\nLast month ({startDate} - {endDate}) stats sent\n')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Retrieve top earning videos within specified date range between any month/year, defaults to current month
    @bot.command(aliases=['getMonth', 'get_month'])
    async def month(ctx, period=datetime.datetime.now().strftime("%m/%Y")):
        period = period.split('/')
        month, year = period[0], period[1]
        year = f'20{year}' if len(year) == 2 else year
        lastDate = monthrange(int(year), int(month))[1]
        startDate = datetime.datetime.strptime(f'{month}/01', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')
        endDate = datetime.datetime.strptime(f'{month}/{lastDate}', '%m/%d').strftime(f'{year}/%m/%d').replace('/', '-')

        try:
            stats = await get_stats(startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\nLast month ({startDate} - {endDate}) stats sent\n')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Retrieve top earning videos within specified date range, defaults to current month
    @bot.command(aliases=['topEarnings', 'topearnings', 'top_earnings'])
    async def top(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            # Get the stats for the specified date range
            stats = await top_revenue(results, startDate, endDate)      
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} top {results} sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Top revenue by country
    @bot.command(aliases=['geo_revenue', 'geoRevenue', 'georevenue'])
    async def detailed_georeport(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)        
        try:
            stats = await top_countries_by_revenue(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\nLast month ({startDate} - {endDate}) geo-revenue report sent\n')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Geo Report (views, revenue, cpm, etc)
    @bot.command(aliases=['geo_report', 'geoReport', 'georeport'])
    async def country(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=3):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_detailed_georeport(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} earnings by country sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Ad Type Preformance Data
    @bot.command(aliases=['adtype', 'adPreformance', 'adpreformance'])
    async def ad(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_ad_preformance(startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} ad preformance sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Demographics Report
    @bot.command(aliases=['demographics', 'gender', 'age'])
    async def demo_graph(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y")):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_demographics(startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])

            print(f'\n{startDate} - {endDate} demographics sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')
    # Shares Report
    @bot.command(aliases=['shares', 'shares_report', 'sharesReport', 'share_report', 'shareReport'])
    async def share_rep(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=5):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_shares(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])

            print(f'\n{startDate} - {endDate} shares result sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Search Terms Report
    @bot.command(aliases=['search', 'search_terms', 'searchTerms', 'search_report', 'searchReport'])
    async def search_rep(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_traffic_source(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} search terms result sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')
            
    # Top Operating Systems
    @bot.command(aliases=['os', 'operating_systems', 'operatingSystems', 'topoperatingsystems'])
    async def top_os(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_operating_stats(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} operating systems result sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Playlist Report
    @bot.command(aliases=['playlist', 'playlist_report', 'playlistReport'])
    async def playlist_rep(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=5):
        startDate, endDate = await update_dates(startDate, endDate)
        try:
            stats = await get_playlist_stats(results, startDate, endDate)
            try:    await ctx.send(embed=stats[0])
            except: pass
            finally: await ctx.send(stats[1])
            print(f'\n{startDate} - {endDate} playlist stats result sent')
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    # Refresh Token
    @bot.command(aliases=['refresh', 'refresh_token', 'refreshToken'])
    async def refresh_API_token(ctx, token=None):
        try:
            status = await refresh(return_embed=True, token=token)
            await ctx.send(embed=status)
        except Exception as e:  await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')

    @bot.command(aliases=['switch', 'devToggle'])
    async def sw_dev(ctx):
        try:
            dev_mode_status = await dev_mode()
            message = f"Dev Mode has been {'enabled' if dev_mode_status else 'disabled'}."
            await ctx.send(message)
        except Exception as e:
            await ctx.send(f'Error:\n{e}\n{traceback.format_exc()}')

    # Send all Commands
    @bot.command(aliases=['everything', 'all_stats', 'allStats', 'allstats'])
    async def all(ctx, startDate=datetime.datetime.now().strftime("%m/01/%y"), endDate=datetime.datetime.now().strftime("%m/%d/%y"), results=10):
        startDate, endDate = await update_dates(startDate, endDate)

        stat_functions = [
            (get_stats, (startDate, endDate)),
            (top_revenue, (results, startDate, endDate)),
            (top_countries_by_revenue, (results, startDate, endDate)),
            (get_ad_preformance, (startDate, endDate)),
            (get_detailed_georeport, (results, startDate, endDate)),
            (get_demographics, (startDate, endDate)),
            (get_shares, (results, startDate, endDate)),
            (get_traffic_source, (results, startDate, endDate)),
            (get_operating_stats, (results, startDate, endDate)),
            (get_playlist_stats, (results, startDate, endDate)),
        ]

        try:
            for stat_function, args in stat_functions:
                result = await stat_function(*args)
                result = result[0] 
                await ctx.send(embed=result)

            print(f'\n{startDate} - {endDate} everything sent')
        except Exception as e:
            await ctx.send(f'Error:\n {e}\n{traceback.format_exc()}')
    
    # Restart Bot Command
    @bot.command(name='restart')
    async def restart(ctx):
        await ctx.send(f"Restarting...\n")
        await bot.close()
        os._exit(0)

    # Bot Pong User's Ping
    @bot.command(name='ping')
    async def ping(ctx):
        await ctx.send('pong')
        print(f'\n{ctx.author.name} just got ponged!\t{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}\n')
    
    # Start Discord Bot
    print(f"Booting up Discord Bot...\n{'-'*150}")
    bot.run(DISCORD_TOKEN)
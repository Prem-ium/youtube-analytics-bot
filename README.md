# 📊 YouTube Analytics Discord Bot 🤖

An awesome Discord bot to retrieve & output your YouTube Analytics data.


## Features & Discord Commands
Start every command with `!`. Optional Command Input is denoted using [brackets]. 

Check [Example Output Folder](https://github.com/Prem-ium/youtube-analytics-bot/blob/main/output-examples/README.MD) for output examples.

#### Start & End Date formats:
- MM / DD Format (MONTH/DATE, Assumes the current year):
```sh
   !stats 01/01 12/01
```
- MM / DD / YYYY Format Example:
```sh
   !stats 01/01/2021 12/31/2021
```
#### Discord Commands:
- YouTube Analytics Report Card. Display Views, Watch-Time, Estimated Revenue, CPM, Ad-Impressions, & more. Defaults to current month if date range not specified📅
```sh
   !stats [startDate] [endDate]
```
- Return stats for a specific month 📆
```sh
   !getMonth [month/year]
```
- Get lifetime stats 🧮
```sh
   !lifetime
```
- Get a list of the highest revenue earning videos on your channel. 💰
```sh
   !topEarnings [startDate] [endDate] [Length to Return]
```
- Get list of your top revenue earning countries 🌎💰
```sh
   !geo_revenue [startDate] [endDate] [Length to Return]
```
- More detailed report of views, revenue, cpm, etc by country 🌎
```sh
   !geoReport [startDate] [endDate] [Length to Return]
```
- Get highest preforming ad types within specified time range 💰
```sh
   !adtype [startDate] [endDate]
```
- Get demographics data (age and gender) of viewers 👨‍👩‍👧‍👧
```sh
   !demographics [startDate] [endDate]
```
- Return list of top sharing methods for your videos. 📤
```sh
   !shares [startDate] [endDate] [Length to Return]
```
- Return YouTube search terms resulting in the most views of your video(s). 🔍
```sh
   !search [startDate] [endDate] [Length to Return]
```
- Return top operating systems watching your videos (ranked by views). 📟
```sh
   !os [startDate] [endDate] [Length to Return]
```
- Return everything. Call every method and output all available data ♾️
```sh
   !everything [startDate] [endDate]
```
- Refresh API Token!
```sh
   !refresh [token]
```
- Switch Dev Mode On/Off
```sh
   !switch
```
- Send all Discord commands with explainations. 🦮
```sh
   !help
```
- Check to make sure bot is running
```sh
   !ping
```
#### Features:
- Docker Support
- Developer Mode
- Analytical Reports delivering information on estimated revenue, cpm, & more
- Refresh Token Ability


#### TODO:
- Replit Support (Get working program without credentials.json or CLIENT_SECRET.json files in directory)
- Google & YouTube Keyword SEO Research Command
- Major Refactor Discord Commands

## Set-Up

#### Google Cloud Console (API Setup)

1. To get started, head over to the Google Cloud Console website and create a new project.
2. Click on 'API & Services' and 'Enable APIs and Services'.
3. Search and enable both 'YouTube Data' and 'YouTube Analytics' API.
4. Return to the API & Services page and click on 'credentials'.
5. Click Create Credentials -> OAuth Credentials -> Desktop Application -> Go through setup.
6. Download the JSON file, name it `CLIENT_SECRET.json` and place the file inside the same folder as the program.
7. Create Credentials -> API Key -> Copy and assign the key to the `YOUTUBE_API_KEY` environment variable.

#### Discord Bot

1. Go to https://discord.com/developers/ and create a new application. Name it YouTube Apprise or whatever you wish, accept the terms.
2. Open the application -> OAuth2 -> URL Generator.
3. Within Scopes, click 'Bot' and enable the desired bot permissions.
4. Enable text permissions such as Send Messages & Read Message History. 
5. Enable general permissions such as View Server Insights.
6. Copy the generated link below Permissions and enter it in a browser. Add the bot to your server of choice (preferably your own private Discord server, as sensitive information such as revenue and CPM is accessible through bot commands).
7. (Optional) Add a pretty profile picture for your bot in Rich Presence.
8. Go to 'Bot' to obtain, reset, and retrieve the token. Assign it to the `DISCORD_TOKEN` environment variable.

## Installation

The bot can be run using Python or Docker.
#### Python Script
1. Clone this repository, cd into it, and install dependancies:
```sh
   git clone https://github.com/Prem-ium/youtube-analytics-bot
   cd youtube-analytics-bot
   pip install -r requirements.txt
   ```
2. Configure your `.env` file (See below and example for options)
3. Run the script:

    ```sh
    python main.py
   ```
#### Docker Container
Build with Docker only after running locally and generating a `credentials.json` file
1. Run script locally with Python to generate credentials json file.
2. Download and install Docker on your system
3. Configure your `.env` file (See below and example for options)
4. To build the image yourself, cd into the repository and run:
   ```sh
   docker build -t youtube-apprise .
   ```
   Then start the bot with:
   ```sh
   docker run -it --env-file ./.env --restart unless-stopped --name youtube-apprise youtube-apprise
   ```
   Both methods will create a new container called `youtube-apprise`. Make sure you have the correct path to your `.env` file you created.

5. Let the bot log in and begin working. DO NOT PRESS `CTRL-c`. This will kill the container and the bot. To exit the logs view, press `CTRL-p` then `CTRL-q`. This will exit the logs view but let the bot keep running.


## Environment Variables:
As always, please refer to the `.env.example' file for examples. 

##### Required .env:
`DISCORD_TOKEN` = Retrieve from https://discord.com/developers/applications


`YOUTUBE_API_KEY` = YouTube Data API Key (Retrieve from Google Cloud Console Credentials's Page after enabling the YouTube Data API)
##### Optional .env:
`CLIENT_PATH` = Path of YouTube/Google Client Secret JSON file. Defaults to current directory (file named "CLIENT_SECRET.json")

`DEV_MODE`= Whether to use experimental features or not. MUST have CLIENT_SECRET configured.

`CLIENT_SECRET`= Contents of CLIENT_SECRET.JSON which includes refresh token value. Check .env.example for a reference. 

`DISCORD_CHANNEL` = Turn on developer mode in advanced settings, right click on text channel, copy ID

`KEEP_ALIVE` = Boolean True/False value. Whether to us a Flask server or not to keep program from dying on platforms like Replit.

## Donations
If you find my project helpful and would like to support its development, please consider making a donation. Every little bit helps and is greatly appreciated!

You can donate by clicking on the following button:
<div style="display:grid;justify-content:center;"><a href="https://www.buymeacoffee.com/prem.ium" target="_blank">
        <img src="https://raw.githubusercontent.com/Prem-ium/youtube-analytics-bot/main/output-examples/media/coffee-logo.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a></div>

Thank you for your support!

## License
This repository uses the [BSD 3-Clause “New” or “Revised” License](https://choosealicense.com/licenses/bsd-3-clause/#)

## Final Remarks
This project was built thanks to YouTube Analytics & Data API Documentation. 
Please leave a :star2: if you found this project to be cool!
May your analytics skyrocket up📈

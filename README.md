# YouTube Analytics Discord Bot
An awesome Discord bot to retireve YouTube Analytics data with ease.

## Set-Up
#### Google Cloud Console (API Setup)
1. To get started, head over to the Google Cloud Console website & create a new project.
2. Click on 'API & Services' & 'Enable APIs and Services'
3. Search & Enable both 'YouTube Data' and 'YouTube Analytics' API.
4. Return to API & Services page and click on 'credentials'
5. Click Create Credentials -> OAuth Credentials -> Desktop Application -> Go through setup.
6. Download JSON, name it `CLIENT_SECRET.json` and place the file inside the same folder as the progran.
7. Create Credentials -> API Key -> Copy and Assign Key to .env variable `YOUTUBE_API_KEY`

#### Discord Bot
1. Go to https://discord.com/developers/ and create a new application. Name it YouTube Apprise or whatever you wish, accept terms.
2. Open the application -> OAuth2 -> URL Generator 
3. Within Scopes, click 'Bot' and within Bot Permissions  
4. Enable Text Permissions such as Send Messages & Read Message History. 
5. Enable General Permissions such as View Server Insights.
6. Copy the generated link below Permissions and enter it in browser. Add the bot to your server of choice (preferably your very own PRIVATE Discord server, as sensitive information such as revenue and CPM is accessibly through bot commands)
7. (Optional) Add a pretty pfp image for your bot in Rich Presence.
8. Return to OAuth2, reset Client Secret, and retrieve the token and assign it to `DISCORD_TOKEN` env variable.

## Installation
The bot can be run using Python & Docker.
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
##### Required .env:
`DISCORD_TOKEN` = Retrieve from https://discord.com/developers/applications


`YOUTUBE_API_KEY` = YouTube Data API Key (Retrieve from Google Cloud Console Credentials's Page after enabling the YouTube Data API)
##### Optional .env:
`DISCORD_CHANNEL` = Turn on developer mode in advanced settings, right click on text channel, copy ID

`KEEP_ALIVE` = Boolean True/False value. Whether to us a Flask server or not to keep program from dying on platforms like Replit.

## Discord Commands
Optional Text is denoted using [brackets]
- `!stats [startDate] [endDate]`- Return stats within time range. Defaults to current month
- `!getMonth [month/year]`- Return stats for a specific month
- `!topEarnings [startDate] [endDate] [# of countries to return (Default: 10)]` - Return top specified highest revenue earning videos.
- `!geo_revenue [startDate] [endDate] [# of countries to return]` - Top Specific (default 10) countries by revenue
- `!geoReport [startDate] [endDate] [# of countries to return]`- More detailed report of views, revenue, cpm, etc by country
- `!adtype [startDate] [endDate]` - Get highest preforming ad types within specified time range
- `!lifetime` - Get lifetime stats
- `!everything [startDate] [endDate]` - Return everything. Call every method and output all available data
- `!help` - Send all commands.
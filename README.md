<p align="right"><a href="https://www.youtube.com/channel/UCTBKWIcBRPGh2yhPkrIbJPw"><img src="https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white" alt="YouTube"/></a></p>
<h1 align="center">📊 YouTube Analytics Discord Bot 🤖 </h1>

<p align="center">An <i>awesome</i> Python Discord Bot to fetch & display your YouTube Analytics data.</p>

<p align="center"><img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/><img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white"/><img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white"/>
   <a href="https://github.com/sponsors/Prem-ium" target="_blank">
        <img src="https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AA" alt="Github Sponsor"/></a>
   <a href="https://www.buymeacoffee.com/prem.ium" target="_blank"> <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"/></a>
   </p>
## Features:
- Collects data on a variety of metrics, including views, revenue, subscriber growth, & more
- Can be used to analyze the performance of a channel and identify areas for improvement
- Discord Button User-Friendly UI
- Docker Support
- Developer Mode
- Efficient API Service Build Methods & Fail-Safe(s)
- Ability to Run 24/7 using Replit & Flask (Dev Mode + Build From Document)

## Input Formatting & Bot Commands:
Start every command with `!`. Optional Command Input is denoted using [brackets]. 

Check [Example Output Folder](https://github.com/Prem-ium/youtube-analytics-bot/blob/main/output-examples/README.MD) for output examples.
- MM / DD Format (MONTH/DATE, Assumes the current year) or MM / DD / YYYY:
```sh
   !stats 01/01 12/01
   !stats 01/01/2021 12/31/2021
```
#### Commands:
| Command | Description |
|---------|-------------|
| `!button [startDate] [endDate]` | Open Discord Button UI with all supported commands |
| `!stats [startDate] [endDate]` | 📅 YouTube Analytics Report Card. Display Views, Watch-Time, Estimated Revenue, CPM, Ad-Impressions, & more. Defaults to current month if date range not specified.  |
| `!getMonth [month/year]` | Return stats for a specific month. 📆 |
| `!lifetime` | Get lifetime stats. 🧮 |
| `!topEarnings [startDate] [endDate] [Length to Return]` | Get a list of the highest revenue earning videos on your channel. 💰 |
| `!geo_revenue [startDate] [endDate] [Length to Return]` | Get a list of your top revenue earning countries. 🌎💰 |
| `!geoReport [startDate] [endDate] [Length to Return]` | More detailed report of views, revenue, cpm, etc by country. 🌎 |
| `!adtype [startDate] [endDate]` | Get highest performing ad types within specified time range. 💰 |
| `!demographics [startDate] [endDate]` | Get demographics data (age and gender) of viewers. 👨‍👩‍👧‍👧 |
| `!shares [startDate] [endDate] [Length to Return]` | Return list of top sharing methods for your videos. 📤 |
| `!search [startDate] [endDate] [Length to Return]` | Return YouTube search terms resulting in the most views of your video(s). 🔍 |
| `!os [startDate] [endDate] [Length to Return]` | Return top operating systems watching your videos (ranked by views). 📟 |
| `!playlist [startDate] [endDate] [Length to Return]` | Retrieve your Playlist Report. |
| `!everything [startDate] [endDate]` | Return everything. Call every method and output all available data. ♾️ |
| `!refresh [token]` | Refresh API Token! |
| `!switch` | Switch Dev Mode On/Off. |
| `!help` | Send all Discord commands with explanations. 🦮 |
| `!ping` | Check to make sure bot is running. |


#### TODO:
- Resend Buttons at Bottom of Embed instead of Editing Stats
- Google & YouTube Keyword SEO Research Command
- Major Refactor Discord Commands

## Set-Up

#### Google Cloud Console (API Setup)

To set up the Google Cloud Console API, follow these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis) website and create a new project.
2. Click on **API & Services** and select **Enable APIs and Services**.
3. Search for and enable both the **YouTube Data API** and **YouTube Analytics API**.
4. Return to the **API & Services** page and click on **Credentials**.
5. Select **User Type (External)**, then configure the **OAuth Consent Screen** by adding the following YouTube Analytics related scopes:
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/yt-analytics-monetary.readonly`
6. Go through the rest of the configuration settings for OAuth.
7. Click **Create Credentials**, then select **OAuth Credentials**, followed by **Desktop Application**. Proceed with the setup.
8. Download the JSON file, name it `CLIENT_SECRET.json`, and place the file inside the same folder as your program. You will be able to optionally assign the contents to the env variable `CLIENT_SECRET` after running the program and generating a refresh token.
9. Create Credentials -> API Key -> Copy and assign the key to the `YOUTUBE_API_KEY` environment variable.

Now your Google Cloud Console API is set up and ready to use!

#### Discord Bot

To set up the Discord bot, follow these steps:

1. Go to [Discord Developers](https://discord.com/developers/) and create a new application. Name it "YouTube Apprise" or any desired name, then accept the terms.
2. Open the created application and navigate to the **OAuth2** URL Generator section.
3. Under **Scopes**, select **Bot** and enable the desired bot permissions.
   - Make sure to enable text permissions like **Send Messages** and **Read Message History**.
   - Additionally, enable general permissions such as **View Server Insights**.
4. Copy the generated link located below the **Permissions** section and paste it into a browser. Use this link to add the bot to your chosen server. It is recommended to add the bot to your own private Discord server to protect sensitive information like revenue and CPM, accessible through bot commands.
5. *(Optional)* Customize the bot's profile picture by adding a visually appealing image in the **Rich Presence** section.
6. In the **Bot** section of the application, obtain, reset, or retrieve the token. Assign this token to the `DISCORD_TOKEN` environment variable.

Now your Discord bot is ready to use!

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
| Environment Variable | Description |
|----------------------|-------------|
| `DISCORD_TOKEN`      | Retrieve from https://discord.com/developers/applications |
| `YOUTUBE_API_KEY`    | YouTube Data API Key (Retrieve from Google Cloud Console Credentials's Page after enabling the YouTube Data API) |

##### Optional .env:
| Environment Variable | Description |
|----------------------|-------------|
| `CLIENT_PATH`        | Path of YouTube/Google Client Secret JSON file. Defaults to current directory (file named "CLIENT_SECRET.json") |
| `DEV_MODE`           | Whether to use experimental features or not. MUST have CLIENT_SECRET configured. |
| `CLIENT_SECRET`      | Contents of CLIENT_SECRET.JSON which includes refresh token value. Check .env.example for a reference. |
| `DISCORD_CHANNEL`    | Turn on developer mode in advanced settings, right click on text channel, copy ID |
| `KEEP_ALIVE`         | Boolean True/False value. Whether to us a Flask server or not to keep program from dying on platforms like Replit. |


## Donations
I've been working on this project for a few months now, and I'm really happy with how it's turned out. It's also been a helpful tool for users to earn some extra money with Bing Rewards. I'm currently working on adding new features to the script and working on other similar programs to generate passive income. I'm also working on making the script more user-friendly and accessible to a wider audience.


I'm accepting donations through <a href="https://github.com/sponsors/Prem-ium">GitHub Sponsors (No Fees!)</a> or <a href="https://www.buymeacoffee.com/prem.ium">Buy-Me-Coffee</a>. Any amount you can donate will be greatly appreciated.
  
<a href="https://github.com/sponsors/Prem-ium" target="_blank">
        <img src="https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA" alt="GitHub Sponsor" img width="15%">
</a>
<a href="https://www.buymeacoffee.com/prem.ium" target="_blank">
        <img src="https://raw.githubusercontent.com/Prem-ium/youtube-analytics-bot/main/output-examples/media/coffee-logo.png" alt="Buy Me A Coffee" img width="15%">
</a>

Your donations will help me to cover the costs of hosting the project, developing new features, and marketing the project to a wider audience.
Thank you for your support!


## License
This repository uses the [BSD 3-Clause “New” or “Revised” License.](https://choosealicense.com/licenses/bsd-3-clause/#)

## Final Remarks
This project was built thanks to YouTube Analytics & Data API Documentation. 
Please leave a :star2: if you found this project to be cool!
May your analytics skyrocket up📈

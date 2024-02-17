<p align="right"><img src="https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white" alt="YouTube"/></p>
<h1 align="center">📊 YouTube Analytics Discord Bot 🤖 </h1>

<p align="center">An <i>awesome</i> Discord Bot to fetch your YouTube Channel Analytics.</p>

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
#### Text Commands:
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

#### Button Supported Commands:
Upon invoking the `!button` command, these are currently supported with a scene containing interactive buttons:
- Analytics
- Top Revenue Videos
- Top Searched Keywords
- Playlist Stats
- Geographic Data
- OS Statistics
- Traffic Source
- Shares
- Top Geographic Based Revenue

## Set-Up
For this project, you need to enable use of Google Cloud Console YouTube Analytics/Data API for your account & create a discord bot to obtain a discord token.
### Google Cloud Console API Setup

Follow these well-organized steps to set up the Google Cloud Console API:

1. **Create a New Project**
   - Visit the [Google Cloud Console](https://console.cloud.google.com/apis) website and create a new project.

2. **Enable APIs and Services**
   - Click on **API & Services** and select **Enable APIs and Services**.

3. **Enable YouTube APIs**
   - Search for and enable both the **YouTube Data API** and **YouTube Analytics API**.

4. **Configure OAuth Consent Screen**
   - Return to the **API & Services** page and click on **Credentials**.
   - Select **User Type (External)**, then configure the **OAuth Consent Screen** by adding the following YouTube Analytics related scopes:
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/yt-analytics-monetary.readonly`

5. **Complete OAuth Configuration**
   - Proceed with the rest of the configuration settings for OAuth.

6. **Create OAuth Credentials**
   - Click **Create Credentials**, then select **OAuth Credentials**, followed by **Desktop Application**. Continue with the setup.

7. **Download OAuth JSON File**
   - Download the JSON file and name it `CLIENT_SECRET.json`.
   - Place this file in the same folder as your program. You'll have the option to assign its contents to the `CLIENT_SECRET` environment variable after running the program and generating a refresh token.

8. **Create API Key**
   - Create Credentials -> API Key.
   - Copy and assign the API key to the `YOUTUBE_API_KEY` environment variable.

Now, your Google Cloud Console API is fully set up and ready to use!


### Discord Bot

Follow these organized steps to set up your Discord bot:

1. **Create a Discord Application**
   - Visit [Discord Developers](https://discord.com/developers/) and create a new application. Name it "YouTube Apprise" or choose a suitable name. Accept the terms.

2. **Configure OAuth2**
   - Access your newly created application and go to the **OAuth2** URL Generator section.

3. **Select Scopes and Permissions**
   - Under **Scopes**, choose **Bot** and enable the required bot permissions.
     - Ensure text permissions like **Send Messages** and **Read Message History** are enabled.
     - Additionally, enable general permissions like **View Server Insights**.

4. **Generate Bot Invite Link**
   - Copy the generated link located beneath the **Permissions** section. Paste this link into your browser. Use it to add the bot to your preferred server. It's recommended to add the bot to your private Discord server to safeguard sensitive information, like revenue and CPM, accessible through bot commands.

5. *(Optional)* **Customize Profile Picture**
   - Enhance your bot's appearance by uploading an appealing image in the **Rich Presence** section.

6. **Retrieve Bot Token**
   - In the **Bot** section of your application, obtain, reset, or retrieve the bot token. Assign this token to the `DISCORD_TOKEN` environment variable.

Now, your Discord bot is ready for action!

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

### Docker Container Setup

Before building the Docker container, follow these steps carefully to ensure a smooth setup. Ensure you have generated the `credentials.json` file locally (unless developer mode is enabled):

1. **Generate Credentials JSON File**
   - Run the Python script locally to generate the `credentials.json` file.

2. **Install Docker**
   - Download and install Docker on your system.

3. **Configure `.env` File**
   - Configure your `.env` file with the necessary settings (see below for options).

4. **Build the Docker Image**
   - To build the image yourself, navigate to the repository directory and execute the following command:
     ```sh
     docker build -t youtube-apprise .
     ```

5. **Start the Bot**
   - Start the bot within a Docker container with the following command:
     ```sh
     docker run -it --env-file ./.env --restart unless-stopped --name youtube-apprise youtube-apprise
     ```
   - Ensure that the path to your `.env` file is correctly specified.

6. **Running the Bot**
   - Once started, the bot will log in and begin its tasks.
   - IMPORTANT: Do NOT press `CTRL-c` as it will terminate the container and the bot. To exit the logs view, use `CTRL-p` followed by `CTRL-q`. This will exit the logs view without stopping the bot.

By following these steps, you'll have a Docker container named `youtube-apprise` running your bot.

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


# Donations

If you appreciate my work and would like to show your support, there are two convenient ways to make a donation:

1. **GitHub Sponsors**
   - [Donate via GitHub Sponsors](https://github.com/sponsors/Prem-ium)
   - This is the preferred donation method as it incurs no transaction fees & different tiers offer perks.
   [![GitHub Sponsor](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA)](https://github.com/sponsors/Prem-ium)

2. **Buy Me A Coffee**
   - [Donate via Buy Me A Coffee](https://www.buymeacoffee.com/prem.ium)
   - [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/prem.ium)

Your generous donations will go a long way in helping me cover the expenses associated with developing new features and promoting the project to a wider audience. I extend my heartfelt gratitude to all those who have already contributed. Thank you for your support!

## License
This repository uses the [BSD 3-Clause “New” or “Revised” License.](https://choosealicense.com/licenses/bsd-3-clause/#)

## Final Remarks
Please leave a :star2: if you found this project to be cool!
Made possible thanks to Google's YouTube Analytics/Data APIs
May your analytics skyrocket up📈

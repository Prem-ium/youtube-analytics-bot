<p align="right">
    <img src="https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white" alt="YouTube"/>
</p>
<h1 align="center">📊 YouTube Analytics Discord Bot 🤖</h1>

<p align="center">
    An <i>awesome</i> Discord Bot to fetch your YouTube Channel Analytics.
</p>

<p align="center">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
    <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white"/>
    <img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white"/>
    <a href="https://github.com/sponsors/Prem-ium" target="_blank">
        <img src="https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AA" alt="GitHub Sponsor"/>
    </a>
    <a href="https://www.buymeacoffee.com/prem.ium" target="_blank">
        <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"/>
    </a>
</p>

---

## Features 🔧
- Collects data on various metrics, including views, revenue, subscriber growth, & more.
- Helps analyze channel performance and identify areas for improvement.
- User-friendly Discord Button UI.
- Docker Support.
- Developer Mode.
- Efficient API Service Build Methods & Fail-Safe(s).
- 24/7 Operation with Replit & Flask (Dev Mode + Build from Document).

### Input Formatting & Bot Commands 🔠
Start every command with `!`. Optional command inputs are denoted with [brackets].

Check [Example Output Folder](https://github.com/Prem-ium/youtube-analytics-bot/blob/main/output-examples/README.MD) for output examples.

- MM / DD Format (MONTH/DATE, assumes current year) or MM / DD / YYYY:
```sh
   !stats 01/01 12/01
   !stats 01/01/2021 12/31/2021
```

### Text Commands 💬
| Command | Description |
|---------|-------------|
| `!button [startDate] [endDate]` | Open Discord Button UI with all supported commands. |
| `!stats [startDate] [endDate]` | 📅 YouTube Analytics Report Card: Displays views, watch-time, estimated revenue, CPM, ad-impressions, & more. Defaults to current month if no date range is specified. |
| `!getMonth [month/year]` | Return stats for a specific month. 📆 |
| `!lifetime` | Get lifetime stats. 🧮 |
| `!topEarnings [startDate] [endDate] [Length to Return]` | Get a list of the highest revenue-earning videos on your channel. 💰 |
| `!geo_revenue [startDate] [endDate] [Length to Return]` | Get a list of your top revenue-earning countries. 🌎💰 |
| `!geoReport [startDate] [endDate] [Length to Return]` | Detailed report of views, revenue, CPM, etc., by country. 🌎 |
| `!adtype [startDate] [endDate]` | Get highest-performing ad types within specified time range. 💰 |
| `!demographics [startDate] [endDate]` | Get demographics data (age and gender) of viewers. 👨‍👩‍👧‍👧 |
| `!shares [startDate] [endDate] [Length to Return]` | Return list of top sharing methods for your videos. 📤 |
| `!search [startDate] [endDate] [Length to Return]` | Return YouTube search terms resulting in the most views of your video(s). 🔍 |
| `!os [startDate] [endDate] [Length to Return]` | Return top operating systems watching your videos (ranked by views). 📟 |
| `!playlist [startDate] [endDate] [Length to Return]` | Retrieve your Playlist Report. |
| `!everything [startDate] [endDate]` | Return everything. Call every method and output all available data. ♾️ |
| `!refresh [token]` | Refresh API Token! |
| `!switch` | Switch Dev Mode On/Off. |
| `!help` | Send all Discord commands with explanations. 🦮 |
| `!ping` | Check if the bot is running. |

### Button Supported Commands 🔘
Upon invoking the `!button` command, these are currently supported with a scene containing interactive buttons:
- Analytics
- Top Revenue Videos
- Top Searched Keywords
- Playlist Stats
- Geographic Data
- OS Statistics
- Traffic Source
- Shares
- Top Geographic-Based Revenue

---

## Set-Up & Installation 🚀
To use this project, enable Google Cloud Console YouTube Analytics/Data API for your account and create a Discord bot to obtain a Discord token.

### Google Cloud Console API Setup 🌐

1. **Create a New Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/apis) and create a new project.

2. **Enable APIs and Services**
   - Go to **API & Services** and select **Enable APIs and Services**.

3. **Enable YouTube APIs**
   - Search for and enable both **YouTube Data API** and **YouTube Analytics API**.

4. **Configure OAuth Consent Screen**
   - Return to **API & Services** page and click on **Credentials**.
   - Select **User Type (External)**, then configure the **OAuth Consent Screen** with these YouTube Analytics-related scopes:
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/yt-analytics-monetary.readonly`

5. **Complete OAuth Configuration**
   - Finish the rest of the OAuth configuration.

6. **Create OAuth Credentials**
   - Click **Create Credentials**, then select **OAuth Credentials**, followed by **Desktop Application**.

7. **Download OAuth JSON File**
   - Download the JSON file and name it `CLIENT_SECRET.json`.
   - Place this file in the same folder as your program.

8. **Create API Key**
   - Create Credentials → API Key.
   - Copy and assign the API key to the `YOUTUBE_API_KEY` environment variable.

Your Google Cloud Console API is now ready!

### Discord Bot Setup 🌐

1. **Create a Discord Application**
   - Go to [Discord Developers](https://discord.com/developers/) and create a new application. Name it "YouTube Apprise" or something suitable.

2. **Configure OAuth2**
   - In your new application, go to the **OAuth2** URL Generator section.

3. **Select Scopes and Permissions**
   - Under **Scopes**, choose **Bot** and enable the required bot permissions, such as **Send Messages** and **Read Message History**.

4. **Generate Bot Invite Link**
   - Copy the generated link from the **Permissions** section and use it to add the bot to your server.

5. *(Optional)* **Customize Profile Picture**
   - Upload an appealing image in the **Rich Presence** section.

6. **Retrieve Bot Token**
   - In the **Bot** section, obtain the bot token and assign it to the `DISCORD_TOKEN` environment variable.

Your Discord bot is now set up!

## Installation 🛠️

The bot can be run using Python or Docker.

### Python Script 🐍

1. Clone this repository, cd into it, and install dependencies:
   ```sh
   git clone https://github.com/Prem-ium/youtube-analytics-bot
   cd youtube-analytics-bot
   pip install -r requirements.txt
   ```

2. Configure your `.env` file (see below for options).
3. Run the script:
   ```sh
   python main.py
   ```

### Docker Setup 🐳

1. **Generate Credentials JSON File**
   - Run the Python script locally to generate the `credentials.json` file.

2. **Install Docker**
   - Download and install Docker.

3. **Configure `.env` File**
   - Configure your `.env` file with the necessary settings.

4. **Build Docker Image**
   ```sh
   docker build -t youtube-apprise .
   ```

5. **Start Bot in Docker Container**
   ```sh
   docker run -it --env-file ./.env --restart unless-stopped --name youtube-apprise youtube-apprise
   ```

6. **Running the Bot**
   - To exit logs without stopping the bot, press `CTRL-p` followed by `CTRL-q`.

---
## Environment Variables 🖥️

Refer to the `.env.example` file for options.

### Required `.env`:
| Environment Variable | Description |
|----------------------|-------------|
| `DISCORD_TOKEN`      | Discord bot token |
| `YOUTUBE_API_KEY`    | YouTube Data API key |

### Optional `.env`:
| Environment Variable | Description |
|----------------------|-------------|
| `CLIENT_PATH`        | Path to YouTube/Google Client Secret JSON file (defaults to current directory). |
| `DEV_MODE`           | Enable experimental features (requires CLIENT_SECRET). |
| `CLIENT_SECRET`      | Contents of `CLIENT_SECRET.json`. |
| `DISCORD_CHANNEL`    | Channel ID for developer mode. |
| `KEEP_ALIVE`         | Boolean value to keep the bot running (e.g., True for Replit). |

---
## Experiencing Issues? 🛠️
As of 9/8/2024, I have disabled the Issues privilege for the general public. For direct support on any bugs or issues, please consider sponsoring me as a GitHub Sponsor under the Silver or Gold tier. 
[![Sponsor](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)](https://github.com/sponsors/Prem-ium)

---
## Donations ❤️
If you appreciate my work, you can donate via:

1. **GitHub Sponsors** - [Donate via GitHub Sponsors](https://github.com/sponsors/Prem-ium).
2. **Buy Me A Coffee**: [Donate via Buy Me A Coffee](https://www.buymeacoffee.com/prem.ium).

---
## License 📝
This repository is licensed under the [BSD 3-Clause License](https://choosealicense.com/licenses/bsd-3-clause/#).

---
## Final Remarks ✨
Please leave a ⭐ if you found this project cool! Made possible by Google's YouTube Analytics/Data APIs. May your analytics skyrocket! 📈

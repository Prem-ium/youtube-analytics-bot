# YouTube Analytics Discord Bot
An awesome Discord bot to retireve YouTube analytics data.

## Installation
(Coming soon... However, if you have the YouTube Analytics API enabled with your Client Secret JSON, you may proceed with installation.)

The bot can be run using Python & Docker.
### Python Script
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
### Docker Container
Build with Docker
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

`DISCORD_CHANNEL` = Turn on developer mode in advanced settings, right click on text channel, copy ID

`YOUTUBE_API_KEY` = YouTube Data API Key (Required for certain commands)
##### Optional .env:
`KEEP_ALIVE` = Boolean True/False value. Whether to us a Flask server or not to keep program from dying on platforms like Replit.

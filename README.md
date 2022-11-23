# YouTube Apprise
A simple Python script to receive notifications of YouTube analytics.

## Future Features

- User-Handled Intervals between messages
- More data involving highest preforming videos

## Possible Future Features / Project Adjustments
- Discord Bot Support / CLI (Command Line) 

## Installation
(Coming soon... However, if you have the YouTube Analytics API enabled with your Client Secret JSON, you may proceed with installation.)

The bot can be run using Python.
### Python Script
1. Clone this repository, cd into it, and install dependancies:
```sh
   git clone https://github.com/Prem-ium/YouTube-Apprise.git
   cd YouTube-Apprise
   pip install -r requirements.txt
   ```
2. Configure your `.env` file (See below and example for options)
3. Run the script:

    ```sh
    python main.py
   ```

## Environment Variables:
`APPRISE_ALERTS` = Notifications and Alerts. See .env example for more details

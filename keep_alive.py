# Full Instructions:
# https://repl.it/talk/learn/Hosting-discordpy-bots-with-replit/11008
# Run this file to keep the bot alive on repl.it

# Enable Keep Alive by using the KEEP_ALIVE variable in .env
# After running, you can copy the URL from the console and paste it into an UptimeRobot
# monitor to keep the bot alive 24/7


from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alivvveee! All thanks to UpTimeRobot! :D"

def run():
    app.run(host = '0.0.0.0', port = 8080)

def keep_alive():
    t = Thread(target = run)
    t.start()
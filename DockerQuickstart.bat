docker stop youtube-apprise
docker rm youtube-apprise

REM Replace the path below with the path to your youtube-analytics-bot folder
cd Desktop\youtube-analytics-bot

docker build -t youtube-apprise .
docker run -itd --env-file ./.env --restart unless-stopped --name youtube-apprise youtube-apprise

REM WARNING: This will remove all dangling images. Uncomment the line below if you want to do this.
REM docker image prune -f --filter "dangling=true"

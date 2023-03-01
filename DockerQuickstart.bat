docker stop youtube-apprise
docker rm youtube-apprise
REM Replace the path below with the path to your youtube-analytics-bot folder
cd Desktop\youtube-analytics-bot
docker build -t youtube-apprise .
docker run -itd --env-file ./.env --restart unless-stopped --name youtube-apprise youtube-apprise
REM WARNING: This will remove all dangling images. If you have other images that you want to keep, do not run this command. Otherwise, run this command to clean up your old docker images.
REM docker image prune -f --filter "dangling=true"

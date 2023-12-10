FROM python:3

ADD requirements.txt /
RUN pip install -r requirements.txt
ADD main.py /
ADD YouTube_API.py /
ADD CLIENT_SECRET.json /
ADD credentials.json /

CMD [ "python", "./main.py"]
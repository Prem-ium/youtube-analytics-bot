FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD main.py /
ADD CLIENT_SECRET.json /
ADD credential_sample.json /
CMD [ "python", "./main.py" ]
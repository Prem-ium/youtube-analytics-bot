FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD main.py /
ADD CLIENT_SECRET.json /
ADD credentials.json /
CMD [ "python", "./main.py"]
#CMD ["python", "./main.py", "--noauth_local_webserver", "--host=0.0.0.0", "--port=8000"]
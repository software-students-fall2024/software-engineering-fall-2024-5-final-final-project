FROM python:3.9-slim-buster

WORKDIR /web-app

RUN pip install pipenv
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY .env .env

ADD . .

# expose the port that the Flask app is running on, by default 5000
EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
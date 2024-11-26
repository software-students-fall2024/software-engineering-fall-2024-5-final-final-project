FROM python:3.10

RUN apt-get update && apt-get install -y \
    ffmpeg \
    flac \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

WORKDIR /project

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

EXPOSE 5050

ENV FLASK_APP=src/app.py

ENV PYTHONPATH= /project

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]

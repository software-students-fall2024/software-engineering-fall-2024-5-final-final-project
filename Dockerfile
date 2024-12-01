FROM python:3.10

RUN apt-get update && apt-get install -y \
    ffmpeg \
    flac \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

WORKDIR /project

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy --dev

COPY . .

EXPOSE 8080

ENV FLASK_APP=src/app.py

ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--debug"]

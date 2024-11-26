FROM python:3.10

RUN pip install pipenv

WORKDIR /project

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy --dev

COPY . .

EXPOSE 8080

ENV FLASK_APP=src/app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]

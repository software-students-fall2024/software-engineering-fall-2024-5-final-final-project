FROM python:3.13

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# ARG MONGO_CXN_STRING
# ARG ML_CLIENT_PORT

CMD ["python", "app.py"]
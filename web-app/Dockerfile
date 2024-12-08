FROM python:3.10

# # Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    python3-dev

# Upgrade pip
RUN python -m pip install --upgrade pip
RUN pip uninstall -y flask jinja2 markupsafe werkzeug itsdangerous
# Rest of your Dockerfile remains the same
WORKDIR /web-app
COPY requirements.txt .
COPY ../recommender /web-app/recommender

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
FROM python:3.10

# Install system dependencies
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

# Set working directory
WORKDIR /web-app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code, including the `recommender` logic
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

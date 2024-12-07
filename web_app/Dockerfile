# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the app files into the container
COPY . /app

# Install system dependencies and Python libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by the Flask app
EXPOSE 5002

# Command to run the Flask app
CMD ["python", "app.py"]

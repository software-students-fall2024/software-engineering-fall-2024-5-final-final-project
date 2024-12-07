# Base Image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /webapp

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile to the container
COPY Pipfile /webapp/

# Run pipenv lock to generate a new Pipfile.lock
RUN pipenv lock

# Install dependencies using the new Pipfile.lock
RUN pipenv install --system --deploy

# Copy the rest of the application code
COPY webapp/ /webapp

# Expose port
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]

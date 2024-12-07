# Base Image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Ensure pipenv is in PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Pipfile to the container
COPY Pipfile /app/

# Run pipenv lock to generate a new Pipfile.lock
RUN pipenv lock

# Install dependencies using the new Pipfile.lock
RUN pipenv install --system --deploy

# Copy the rest of the application code
COPY . /app/

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]

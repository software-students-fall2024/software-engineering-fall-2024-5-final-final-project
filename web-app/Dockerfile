# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /web-app

# Install necessary system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0  # Add libglib2.0-0 to fix libgthread-2.0.so.0 issue

# Upgrade pip and install pipenv
RUN python -m pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv
RUN pipenv install --python $(which python3) --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 5000

# Set the command to run the web app
CMD ["pipenv", "run", "python", "app.py"]

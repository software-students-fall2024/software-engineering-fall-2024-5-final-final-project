# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install the required Python dependencies
RUN pip install --no-cache-dir flask requests

# Expose the port Flask will run on
EXPOSE 5000

# Set the command to run the Flask app
CMD ["python", "app.py"]

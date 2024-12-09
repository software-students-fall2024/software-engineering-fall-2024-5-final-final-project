# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ../requirements.txt .
RUN apt-get update && \
    apt-get install -y gcc g++ make && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the application port
EXPOSE 5002

# Set the command to run the application
CMD ["python", "bar_recs.py"]

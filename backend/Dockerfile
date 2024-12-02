# Use an official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies directly using pip
RUN pip install --no-cache-dir fastapi uvicorn pymongo python-dotenv

# Copy the application code
COPY . .

# Expose the application's port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

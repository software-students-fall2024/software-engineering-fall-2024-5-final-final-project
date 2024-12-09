# Use Python base image
FROM python:3.9

# Set the working directory in the image
WORKDIR /app

# Install dependencies into the image
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Add files from your local machine into a Docker image
# Copy the current directory contents into the container at /app
ADD . .

# Expose the port that the Flask app is running on
EXPOSE 5001

# Set the environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5001
ENV FLASK_ENV=development

# Run app.py when the container launches
CMD [ "flask", "run", "--host=0.0.0.0" ]

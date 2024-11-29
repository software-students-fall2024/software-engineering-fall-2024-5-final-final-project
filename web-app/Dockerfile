# use the Python image as a base - version Python 3.10
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install -r requirements.txt

# Install NLTK and download punkt tokenizer data
RUN pip install --no-cache-dir nltk
RUN python -m nltk.downloader punkt punkt_tab

# Copy the application files into the container
COPY . .

# Expose the port the Flask app will run on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
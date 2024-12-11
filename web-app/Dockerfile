FROM python:3.9-slim

# WORKDIR /app
WORKDIR /app
#COPY . .

#RUN pip3 install --no-cache-dir -r requirements.txt

#EXPOSE 5000

#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]
##CMD ["python", "web-app/app.py"]

#newone
# Copy the rest of the application code
COPY . /app/

# Expose Flask port
EXPOSE 5000
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# Command to run the Flask application
# Ensure FLASK_APP is properly set and Python runs the Flask app
ENV FLASK_APP=app.app:create_app

# Run the Flask app on container start
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

FROM python:3.9-slim

WORKDIR /app

# COPY . .

# RUN pip3 install --no-cache-dir -r requirements.txt

# EXPOSE 5000

# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]

WORKDIR /web-app
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
RUN pip3 install --no-cache-dir -r requirements.txt


# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

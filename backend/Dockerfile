FROM python:3.8-slim-buster
# Set working directory to parent of backend
WORKDIR /src
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
# Copy backend directory specifically
COPY . /src/backend
# Add src to Python path so 'backend' module can be found
ENV PYTHONPATH=/src
EXPOSE 5001
# Run main.py from the backend directory
CMD ["python", "backend/main.py"]
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    python3-dev

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install dependencies in specific order
RUN pip install numpy scipy cython


# Install scikit-surprise with verbose output and force compilation
RUN pip install --verbose --no-binary :all: scikit-surprise

# Rest of your Dockerfile remains the same
WORKDIR /web-app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
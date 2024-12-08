# SplitSmart

[![CI / CD](https://github.com/software-students-fall2024/5-final-whats-your-linkedin/actions/workflows/build.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-whats-your-linkedin/actions/workflows/build.yml)

![event-logger](https://github.com/software-students-fall2024/5-final-whats-your-linkedin/actions/workflows/event-logger.yml/badge.svg)

**SplitSmart** is a group expense management application, enabling users to effortlessly create groups, add expenses, and evenly split costs among members. This makes it simple to settle shared expenses for trips, events, and more.


## Links to the container image

Container images for webapp hosted on dockerhub: https://hub.docker.com/r/popilopi/webapp


## Teammates

[Hugo Bray](https://github.com/BringoJr)

[Ethan Cheng](https://github.com/ethanhcheng)

[Jessica Xu](https://github.com/Jessicakk0711)

[Hang Yin](https://github.com/Popilopi168)


## Installation
To set up this project locally, follow these steps:

1. **Clone the repository** (or download the files):
    ```bash
    git clone https://github.com/software-students-fall2024/5-final-whats-your-linkedin.git
    cd <repository-folder>
    ```

2. **Create a virtual environment**:
    - make sure to create `.env` file under both `web-app` and `machine-learning-client` folder
    - create a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    cd webapp/
    pip install -r requirements.txt
    ```


4. **Build using Docker**:
    ```bash
    docker build -t webapp .
    docker run -p 5001:5000 webapp
    ```

    - This will start the Flask app inside the container and map it to port 5001 on your host machine. You can access the application at http://127.0.0.1:5001/. 
[![Run WebApp Test](https://github.com/software-students-fall2024/5-final-y2k/blob/main/.github/workflows/testing.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-y2k/blob/main/.github/workflows/testing.yml)
 [![Run MongoDB Tests](https://github.com/software-students-fall2024/5-final-y2k/blob/main/.github/workflows/publishing.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-y2k/blob/main/.github/workflows/publishing.yml) 
# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Project Name

y2k 

This project utilizes a Docker container to streamline deployment and functionality.  
The container image for this project is available on DockerHub:

[**Container Image on DockerHub**](https://hub.docker.com/r/lucaignatescu/y2k-final-project)

## Table of Contents
1. [Project Description](#project-description)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Task Board](#task-board)
8. [Team Members](#team-members)
9. [Acknowledgements](#acknowledgements)

### Project Description 

An Audio Recording & Transcription App

Record and save your audio files, share them with friends, and get automatic transcriptions. Perfect for notes, interviews, or anything you need! 

### Features

- **Audio Recording & Storage**: Record and save audio files directly within the app.  
- **Speech-to-Text Transcription**: Automatically transcribe recordings into text for easy accessibility.  
- **File Privacy Options**: Set recordings as public or private to manage visibility.  
- **File Management**: Edit, rename, or delete audio files and transcriptions.  
- **User Authentication**: Secure registration and login system with password hashing.  
- **File Sharing**: Share public audio files with others seamlessly.  
- **Metadata Tracking**: Store detailed metadata, including upload time and user information.
- **Environment: Runs** Run Seamlessly in containerized environments using Docker

### Technologies Used

- **Languages**: Python (Flask for backend), JavaScript, HTML/CSS.  
- **Frameworks & Libraries**: Flask, Flask-Login, PyMongo, GridFS, Pydub, SpeechRecognition.  
- **Databases**: MongoDB (GridFS for audio file storage).  
- **Tools**: Docker for containerized deployment, pipenv for dependency management.  
- **CI/CD**: GitHub Actions for automated testing and deployment workflows.

## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/software-students-fall2024/5-final-y2k.git
cd 5-final-y2k
```

### 2. Install pipenv

```
pip install pipenv
```

### 3. Install dependencies

```
pipenv install
```

### 4. Activate the shell

```
pipenv shell
```
### 5. Build and run docker containers

Create a .env file 

```
MONGODB_USERNAME= abc123
MONGODB_PASSWORD= abc123
FLASK_SECRET= abc123
```

### 6. Build and run docker containers

```
docker compose up
```

### 7. Stop docker containers

```
docker compose down
```

### Usage

1. Build and launch app using instructions above for setup
2. Access at http://localhost:8080/ 
3. Start session and record through the web app
4. View the public and private session details

## Project Structure

```text
.
├── __pycache__
├── .github
│   ├── workflows
│   │   ├── event-logger.yml
│   │   ├── publishing.yml
│   │   └── testing.yml
├── data
├── static
│   ├── grid.css
│   ├── record-player.png
│   ├── recording.js
│   ├── styles.css
│   └── Welcome.png
├── templates
│   ├── edit_transcription.html
│   ├── index.html
│   ├── login.html
│   ├── public_files.html
│   ├── record.html
│   ├── register.html
│   └── user_files.html
├── test
│   └── test_test.py
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── instructions.md
├── LICENSE
├── pipfile.
├── pipfile.lock
├── pyproject.toml
└── README.md
```

## Task Boards
[The Task board for our team](https://github.com/orgs/software-students-fall2024/projects/153)

## Team Members
- [Luca Ignatescu (li2058)](https://github.com/LucaIgnatescu)
- [Neha Magesh (nm3818)](https://github.com/nehamagesh)
- [Nuzhat Bushra(ntb5562)](https://github.com/ntb5562)
- [Tamara Bueno (tb2803)](https://github.com/TamaraBuenoo)

## Notes

This project is meant to be run on Google Chrome. Additionally, for an accurate transcription, please wait 10 seconds before and between starting the recording. [Pro Tip: Wait for all the Docker Containers to Run]

## Acknowledgements 

We used online tutorials and forums.

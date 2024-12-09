![Web App Build/Test](https://github.com/software-students-fall2024/4-containers-hej4/actions/workflows/web-app.yml/badge.svg)

# Happylist

## Table of Contents
1. [Description](#description)
2. [Configure](#configure)
3. [Run the app](#run-the-app)
4. [Tests](#testing)
5. [Container Images](#container-images)
6. [Digital Ocean Deployment](#deployment)
7. [Team members](#team-members)

## Description
This app allows users to create and share shopping wish lists. It uses Docker and MongoDB, operating in a containerized environment with two subsystems: a database and a custom web-app. It also features deployment and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Configure
Create a .env file to store key-value pairs (provided in the discord channel).

Clone the repository:
```
git clone https://github.com/software-students-fall2024/5-final-hej5.git
cd 5-final-hej5
```

## Run the app
Start by building:
```
docker-compose up --build
```

Or if you have previously built and haven't made any changes, simply compose the containers:
```
docker-compose up
```

Open the web app following this link [HERE](http://127.0.0.1:5001)

When finished using the app, stop and remove the containers and previously created resources:
```
docker-compose down
```

## Testing
The web-app subsystem includes unit tests with 80+% code coverage. Run the tests with pytest:
```
cd web-app
pytest --cov=.
```

## Container Images
[Flask Web-App Image](https://hub.docker.com/r/jnahan/happylist)
[MongoDB Image]()
<!-- INSERT CONTAINER LINK -->

## Digital Ocean Deployment
See our web-app deployment using Digital Ocean [HERE]()
<!-- INSERT DEPLOYMENT LINK -->

## Team members
[Haley Hobbs](https://github.com/haleyhobbs) \
[Emma Zhu](https://github.com/ez106) \
[Jason Tran](https://github.com/huyy422) \
[Jenna Han](https://github.com/jnahan)

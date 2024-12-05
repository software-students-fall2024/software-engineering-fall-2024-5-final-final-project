![Web App Build/Test](https://github.com/software-students-fall2024/4-containers-hej4/actions/workflows/web-app.yml/badge.svg)
<!-- finish badge -->
# Happylist

## Table of Contents
1. [Description](#description)
2. [Configure](#configure)
3. [Run the app](#run-the-app)
4. [Container Images](#container-images)
4. [Team members](#team-members)

## Description
This app allows users to create and share shopping wish lists. It uses Docker and MongoDB, operating in a containerized environment with two subsystems. It also features deployment and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Configure
Create a .env to store key-value pairs (provided in the discord channel).

## Run the app
Start by building
```
docker-compose up --build
```

Or if you have previously built and haven't made any changes, simply compose the containers
```
docker-compose up
```

Open the web app following this link [HERE](http://127.0.0.1:5001)

## Container Images
<!-- links -->
## Team members

[Haley Hobbs](https://github.com/haleyhobbs) \
[Emma Zhu](https://github.com/ez106) \
[Jason Tran](https://github.com/huyy422) \
[Jenna Han](https://github.com/jnahan)
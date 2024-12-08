# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

# Build Badge

[![Backend CI / CD](https://github.com/software-students-fall2024/5-final-super-awesome-team-name-2/actions/workflows/backend.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-super-awesome-team-name-2/actions/workflows/backend.yml)

[![Frontend CI/CD](https://github.com/software-students-fall2024/5-final-super-awesome-team-name-2/actions/workflows/frontend.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-super-awesome-team-name-2/actions/workflows/frontend.yml)

## Description

Our Personal Finance Tracker is a web application meant to assist users in managing their finances. The application will help users:

- Log in securely and manage their personal profiles
- Set and update budgets
- Track their expenses
- View remaining budgets and total expenses
- Predict next month’s expenses based on historical data using a built-in machine learning model

It's built with Python and Flask. The application utilizes a MongoDB database to securely store user data and transaction histories. It's also containerized using Docker, making sure there's consistent deployment across differing environments. We also have unit tests included to maintain code quality and reliability.

## Subsystems

This project consists of two main subsystems:

1. **Backend**:
   - A Flask-based RESTful API for user authentication, financial data management, and machine learning predictions
   - Interacts with a MongoDB database to store user and transaction data
   - Fully containerized with its own `Dockerfile` and an integrated CI/CD pipeline

2. **Frontend**:
   - A Flask app serving a user-friendly interface
   - Proxies API requests to the backend for seamless integration
   - Includes interactive forms and modals for updating budgets and managing expenses

## Setup Instructions

### Prerequisites

1. Install Docker and Docker Compose.
2. Ensure MongoDB is running locally or available as a service.


### Running the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/software-students-fall2024/5-final-super-awesome-team-name-2.git
   cd 5-final-super-awesome-team-name-2
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

3. Access the application:


## Starter Data

To initialize the database with starter data:
1. Run the backend container and access its shell:
   ```bash
   docker exec -it backend-container-name bash
   ```
2. Execute the following script:
   ```python
   from backend.database import Database
   db = Database()
   db._ensure_default_user()
   ```

## Team members

- [Darren Zou](https://github.com/darrenzou)
- [Peter D'Angelo](https://github.com/dangelo729)
- [Gene Park](https://github.com/geneparkmcs)
- [Joseph Chege](https://github.com/JosephChege4)

# Acknowledgements

- Each of the following links is a source we looked at during the completion of this assignment
    - [Folder Structure](https://studygyaan.com/flask/best-folder-and-directory-structure-for-a-flask-project)
    - [Flask Configuration](https://codingnomads.com/python-flask-app-configuration-project-structure)
    - [Flask Stucture and Blueprints](https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy)
    - [Flask with MongoDB and Docker](https://www.digitalocean.com/community/tutorials/how-to-set-up-flask-with-mongodb-and-docker)
    - [Flask Login](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login)
    - [Bcrypt](https://pypi.org/project/bcrypt/)
    - [More Bcrypt](https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/)
    - [Flask Pytest](https://testdriven.io/blog/flask-pytest/)
    - [More Pytest](https://www.geeksforgeeks.org/pytest-tutorial-testing-python-application-using-pytest/)
    - [Scikit Learn](https://scikit-learn.org/dev/modules/generated/sklearn.linear_model.LinearRegression.html)
    - [Machine Learning and Flask](https://www.analyticsvidhya.com/blog/2020/04/how-to-deploy-machine-learning-model-flask/)
    - [More Machine Learning and Flask](https://33rdsquare.com/integrating-machine-learning-into-web-applications-with-flask/)
    - [Example Code for ML with Flask](https://github.com/2003HARSH/House-Price-Prediction-using-Machine-Learning)
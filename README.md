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

Outside of MongoDB, this project consists of two main subsystems:

1. **Backend**:
   - Flask-based and for user authentication, financial data management, and machine learning predictions
   - Interacts with a MongoDB database to store user and transaction data
   - Fully containerized with its own `Dockerfile` and an integrated CI/CD pipeline
   - Custom queries in MongoDB are implemented to fetch and aggregate data efficiently
   - /health-check: Monitors the health of the backend service
   - /data-cleanup: Cleans up temporary or unused records periodically (admin-only access)

2. **Frontend**:
   - A Flask app serving a user-friendly interface
   - Proxies API requests to the backend for seamless integration
   - Includes interactive forms and modals for updating budgets and managing expenses
   - Modals displays detailed breakdowns of expenses by category 
   - Interactive pie charts powered by Chart.js

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
   You can access the application through Digital Ocean using the following link: [http://68.183.21.82:5000/](http://68.183.21.82:5000/).


## Starter Data (Optional)

Starter data can be used in the app if the user wishes.
To initialize the database with starter data:
1. Run the backend container and access its shell:
   ```bash
   docker exec -it backend-container-name bash
   ```
   Where backend-container-name is the name of the backend container. 
   You can see all docker container names with the docker command:
   ```
   docker ps
   ```

2. Execute the following script (also saved in backend folder as script.sh):
   ```python
   from backend.database import Database
   db = Database()
   db._ensure_default_user()
   ```

## Using App

Make sure all steps in Running Project section is completed then the user can log in with the following steps.

1. Go to: http://localhost:5000/ (or http://68.183.21.82:5000/ for Digital Ocean version) in browser

2. The default username and password is 'user' and 'pw' respectively or create an account with Create Account button.

3. You can add expenses and update budgets with the add expense button and update budget button in the app.

4. You can see a list of expenses in the view expense button.


## Extended Testing Strategies
We have implemented comprehensive testing but noted edge cases and advanced scenarios that required more focus:

1. Database Mock Testing:

   Used mongomock to simulate database operations during unit testing.
   Test cases cover CRUD operations for expenses and user profiles.

2. Performance Edge Cases:

   Stress-tested the backend to handle high volumes of requests. For example, testing scenarios where 1,000+ expense records are processed at once.

3. Authentication Scenarios:

   Includes cases for token expiry, invalid login attempts, and user session management failures.

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
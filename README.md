# Final Project: Wish List Tracker App

![Flask API CI/CD Badge]()
![MongoDB CI/CD Badge]()

## Table of Contents
- [Project Description](#project-description)
- [Subsystems Overview](#subsystems-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Contributors](#contributors)
- [Links](#links)
- [Future Work](#future-work)

---

## Project Description
The Wish List Tracker App is a web-based platform designed to help users organize, share, and manage their wishlists for any occasion. Users can create multiple wishlists, add items with detailed information (e.g., name, price, purchase link), and share these lists with friends and family. The app aims to simplify gift-giving while avoiding duplicate gifts through a "claim" feature. 

**Target Audience:** 
- Individuals organizing wishlists for personal use.
- Families and friends looking to streamline gift exchanges.

**Key Features:**
- Wishlist creation and management.
- Sharing wishlists via unique links.
- Item claiming to prevent duplicate purchases.
- (Future) Item recommendations based on wishlist contents.


---

## Subsystems Overview

### Subsystem 1: Flask API
- **Description:** The Flask API serves as the backend of the application, providing endpoints for user authentication, wishlist management, and item claiming. It integrates with the MongoDB database to store and retrieve data.
- **Technology Stack:** Python, Flask, MongoDB
- **Container:** [Link to Docker Hub image] (To be added)

### Subsystem 2: MongoDB Database
- **Description:** The MongoDB database stores all application data, including user profiles, wishlists, and items. It ensures data persistence and allows for efficient querying.
- **Technology Stack:** MongoDB
- **Container:** [Link to Docker Hub image] (To be added)


---

## Getting Started

### Prerequisites
- [List any dependencies, tools, or technologies needed to run the project, e.g., Docker, Python, MongoDB.]

### Setup Instructions
1. Clone the repository:
    ```bash
    git clone https://github.com/software-students-fall2024/5-final-fantastic-five.git
    ```
2. Navigate to the project directory:
    ```bash
    cd wishlist-tracker <!-- temp, not actual name -->
    ```
3. Follow the setup instructions for each subsystem:
    - **Flask API:**
        ```bash
        cd api
        docker build -t flask-api . <!-- temp, not actual name -->
        docker run -d -p 5000:5000 flask-api <!-- temp, not actual port -->
        ```
    - **MongoDB:**
        ```bash
        docker pull mongo
        docker run -d -p 27017:27017 --name mongodb mongo <!-- temp, not actual port -->
        ```
---

## Usage
Once the application is set up, update the following steps:
1. Access the Flask API endpoints for managing wishlists and items (e.g., `http://localhost:5000/wishlists`). <!-- temp, not actual name -->
2. Create wishlists by sending POST requests to the `/wishlists` endpoint. <!-- temp, not actual name -->
3. Share wishlists by using the generated unique links.

---

## Environment Variables
<!-- temp, not actual name -->
The application requires the following environment variables:
- `DB_HOST`: Host for the MongoDB database (e.g., `localhost` or the container name in Docker).
- `DB_PORT`: Port for the MongoDB database (default: `27017`).
- `DB_NAME`: Name of the database (e.g., `wishlist_db`).
- `SECRET_KEY`: Secret key for Flask sessions.

---

## Testing
Each subsystem includes unit tests to ensure functionality.

<!-- temp, not actual commands, just for example -->
### Running Tests
1. **Subsystem 1:**
    ```bash
    cd api
    pytest --cov=.
    ```
2. **Subsystem 2:**
    ```bash
    cd subsystem2
    pytest --cov=.
    ```

---

## Contributors
- [Alexandra Mastrangelo](https://github.com/alexandramastrangelo)
- [Natalie Trump](https://github.com/nht251)

---

## Links
- [Container Images](#)
  - [Subsystem 1 Image](https://hub.docker.com/r/yourusername/subsystem1)
  - [Subsystem 2 Image](https://hub.docker.com/r/yourusername/subsystem2)
- [Digital Ocean Deployment](#)
  - [Subsystem 1 Deployment](#)
  - [Subsystem 2 Deployment](#)

---

## Future Work
- **Item Recommendations:** Suggest items based on wishlist content.
- **Collaborative Wishlists:** Allow multiple users to contribute to a single wishlist.
- **Price Tracking:** Notify users of price changes for wishlist items.

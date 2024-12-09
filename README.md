![System1](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/FILE-NAME.yml/badge.svg)

![System2](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/FILE-NAME.yml/badge.svg)

![Lint-free](https://github.com/nyu-software-engineering/5-final-finalfour/actions/workflows/lint.yml/badge.svg)

# NYC BAR RECOMMENDER SYSTEM

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## TABLE OF CONTENTS

1. [Description](#description)
2. [Links to Container Images](#container-images)
3. [Setup Steps](#setup-steps)
4. [Team Members](#team-members)

## DESCRIPTION
Home-Brewed Web Application

Home-Brewed is a web application designed to help users manage and explore their favorite bars based on personalized preferences. It provides a seamless user experience for adding, searching, sorting, editing, and receiving bar recommendations.

Key Features

	1.	User Authentication:
	•	Includes a logout feature to ensure secure user sessions.
	2.	Intuitive Navigation:
	•	A clean and organized navigation bar allows users to easily switch between key functionalities like Home, Add, Edit/Delete, Search, Sort, and Recommendations.
	3.	Add New Bars:
	•	Users can contribute by adding their favorite bars to the database, complete with details like bar name, type, occasion, area, reservation availability, and cost.
	4.	Edit/Delete Existing Bars:
	•	Modify or remove existing entries to keep the data up-to-date and relevant.
	5.	Search for Bars:
	•	Quickly find bars that match specific criteria or keywords.
	6.	Sort Bars:
	•	Organize bars based on preferences such as cost, type, or occasion.
	7.	Personalized Recommendations:
	•	Displays a curated list of bars tailored to user preferences, including details like type, occasion, area, reservation status, and cost.
	•	If no recommendations are found, users are prompted to add new bars.
## CONTAINER IMAGES

## SETUP STEPS

**1. Clone the Repository**

```
git clone <[repository-url](https://github.com/software-students-fall2024/5-final-finalfour)>
cd <5-final-finalfour>
```

**2. Verify MongoDB Connection:**

- _Download MongoDB:_ download this extension onto your chosen source code editor
- _Connect to Database URL:_ mongodb://mongodb:27017/

**3. Go to Correct Filepath:**

- _Mac:_

  ```
  cd Desktop/5-final-finalfour-main/web-app
  ```

- _Windows:_
  ```
  cd Desktop\5-final-finalfour-main\web-app
  ```

**4. Create a Virtual Environment:**

- _Mac:_

  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- _Windows:_
  ```
  python3 -m venv .venv
  .venv\Scripts\activate
  ```

**5. Install Dependencies:**

```
pip install opencv-python-headless
pip install pytest pytest-cov
pip install requests
pip install pymongo
pip install -r requirements.txt
```

**6. Install Docker-Compose:**

```
brew install docker-compose
```

**7. Integrate with Docker Compose:**

```
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

**8. Get Drinking!:** Access our NYC Bars Recommender System [here](http://127.0.0.1:5888)!

We cannot get Digital Ocean to work so to use or Recommender System locally run the following commands:

```
export FLASK_APP=web-app/app.py 

flask run
```

## TEAM MEMBERS

- [Wenli Shi](https://github.com/WenliShi2332)
- [Alex Hsu](https://github.com/hsualexotake)
- [Reese Burns](https://github.com/reeseburns)
- [Emily Huang](https://github.com/emilyjhuang)

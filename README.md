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

## CONTAINER IMAGES

## SETUP STEPS

**1. Clone the Repository**
```
git clone <[repository-url](https://github.com/software-students-fall2024/5-final-finalfour)>
cd <5-final-finalfour>
```

**2. Verify MongoDB Connection:**
- *Download MongoDB:* download this extension onto your chosen source code editor
- *Connect to Database URL:* mongodb://mongodb:27017/

**3. Go to Correct Filepath:**
- *Mac:*
   ```
   cd Desktop/5-final-finalfour-main/web-app
   ```

- *Windows:*
   ```
   cd Desktop\5-final-finalfour-main\web-app
   ```

**4. Create a Virtual Environment:**
- *Mac:*
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

- *Windows:*
   ```
   python3 -m venv .venv
   .venv\Scripts\activate
   ```

**5. Install Dependencies:**
```
pip install requests
pip install pymongo
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

## TEAM MEMBERS

- [Wenli Shi](https://github.com/WenliShi2332)
- [Alex Hsu](https://github.com/hsualexotake)
- [Reese Burns](https://github.com/reeseburns)
- [Emily Huang](https://github.com/emilyjhuang)

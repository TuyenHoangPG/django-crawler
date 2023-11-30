# Django Crawler Example

### Project structure

This folder is divided in:

```
├── common                         # contain common module for the project like configs, constant, etc.
├── crawler                        # core module, include settings, urls,...
├── logs                           # save api daily logs
├── modules                        # contain all app module like auth, user, property,...
├── requirements                   # necessary dependencies
├── static                         # contain static files
├── templates                      # template html, template email

```

## Editor

- Visual studio code
- Extension: https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter

## Local Run

### Prepare env and package

- Create file `.env` simular with file `.env.example`
- Replace environment key with your environment value
- Install packages using `pipenv`

```
# pipenv shell
# pipenv install
```

- Or install packages using requirements

```
# python3 -m venv venv
# source venv/bin/activate
# pip3 install -r requirements/requirements.txt
```


### Setup Database

- Install posgresql
- Run migration 

```
# python manage.py migrate
```

### Run App

- Run App

```
# python manage.py runserver
```

## Docker Run
### Prepare env

- Create file `.env` simular with file `.env.example`
- Replace environment key with your environment value

### Build image and run container
- Build image
```
# docker compose -f docker-compose.yaml build
```

- Run container
```
# docker compose -f docker-compose.yaml up
```

### To run migration inside docker container
```
# docker ps  -> to get api container name
# docker exec -it {api-container-name} /bin/bash
# python manage.py migrate
```

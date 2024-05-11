# Django-book-API

This is a project to demostrate the usage of Django in implementing a RESTful
API together wiht user authentication and sessions handling.

## Installation

This project uses [Poetry](https://python-poetry.org/) as package manager, to install it if you dont have it installed, please follow [this instractions](https://python-poetry.org/docs/) to install it before running the app.

The python version required for this app is **3.11**, you can install [pyenv](https://github.com/pyenv/pyenv) to manage your local python version

The project uses [Postgres](https://www.postgresql.org/) as its database, make sure you have installed it on your PC. You can find the enviromental variables needed for this project in `env.template`

After cloning the repository, run:

```
poetry install
```

to install all dependecies

Then, run:

```
cd myBookList
```

```
poetry run python manage.py makemigrations
```

```
poetry run python manage.py migrate
```

The above lines makes the necesary migrations to the database

After that, run:

```
poetry run python manage.py runserver
```

to start the server

## API Documentation:

You can find the Postman API documentation [here](https://documenter.getpostman.com/view/26969282/2sA3JM8hRi)

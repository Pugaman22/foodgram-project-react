# Recipe book 'Foodgram'

## Project description

#### Available features for users:
- publish recipes
- subscribe to recipe authors
- add your favorite recipes to the “Favorites” list
- download a list of products for shopping

## Technology stack
![Static Badge](https://img.shields.io/badge/Python-4.2.5-blue)
![Static Badge](https://img.shields.io/badge/Django-4.2.5-blue)
![Static Badge](https://img.shields.io/badge/DRF-3.14.0-blue)
![Static Badge](https://img.shields.io/badge/djoser-2.2.0-blue)
![Static Badge](https://img.shields.io/badge/gunicorn-21.2.0-blue)
![Static Badge](https://img.shields.io/badge/psycopg2--binary-2.9.8-blue)
![Static Badge](https://img.shields.io/badge/Docker-blue)

## Installation and running
- Cloning the remote repository
  
  ```
  git@github.com:Pugaman22/foodgram-project-react.git
  ```
  ```
  cd backend
  ```
- Create .env and fill it with data from env.example
  ```
  touch .env
  ```
- Running the project
  ```
  cd infra
  ```
  ```
  docker compose up -d
  ```
  ```
  docker compose exec backend python manage.py makemigrations
  ```
  ```
  docker compose exec backend python manage.py migrate
  ```
  ```
  docker compose exec backend python manage.py collectstatic
  ```
  ```
  docker compose exec backend python manage.py ingr_import
  ```
  ```
  docker compose exec backend python manage.py createsuperuser
  ```
- Open a link
  ```
  http://localhost/
  ```
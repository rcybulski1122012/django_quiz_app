# Django quizzes app

Simple application made with Python and Django, which allows you to create and
take quizzes. Created for educational purposes.

[Live version](https://django-quizzes-app.herokuapp.com/)

## Features
* Creating, editing, deleting and taking quizzes
* Sorting quizzes by a date of creation, a number of questions, or an average score
* Filtering quizzes by an author or a category
* Creating accounts, updating a profile, changing and resetting a password 

## Technologies
* Python 3.8
* Django 3.1
* Bootstrap 4

## Setup
1. Clone the repository
```sh
$ git clone https://github.com/rcybulski1122012/django_quiz_app.git
```

2. Create virtual environment, activate it and install dependencies
```sh
$ cd django_quiz_app
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

3.Run migrations and create a super user
```sh
$ python manage.py migrate
$ python manage.py createsuperuser
```

4. Provide default photos in media directory: `default-profile.jpg` and `default-quiz.jpg`

5. Load required fixture
```sh
$ python manage.py loaddata fixtures/required.json
```

6. That's all. Now you can run the application
```sh
$ python manage.py runserver
```

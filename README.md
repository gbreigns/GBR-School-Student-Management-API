# The School REST API is designed to allow school personnel to create accounts and oversee student information through a web app powered by PythonAnywhere. The API offers CRUD functionality for student data and features a user-friendly Swagger UI for testing and integration with the app's frontend.

The app restricts students to a limited set of actions, such as updating their personal information and viewing their profiles, courses, grades, and CGPA.

This Python Flask-RESTX-based API for managing students was developed by Gbreigns a Backend Engineering student at AltSchool Africa.

A Student Management API built with Python (Flask)




## Live ( deployed version ) 

Visit [website](http://Gbreigns.pythonanywhere.com/)

## Testing Locally

Clone the repository

```console
git clone https://github.com/gbreigns/GBR-School-Student-Management-API.git
```

Change directory to the cloned folder

```console
cd GBR-School-Student-Management-API
```

Install necessary dependencies to run the project

```console
pip install -r requirements.txt
```
Create database from migration files 

```console
flask db migrate -m "your description"
```

```console
flask db upgrade
```
Run application

```console
python runserver.py
```
To test routes:

- Create a new admin account with the auth/register route. Registration code for creating admin (reg_code) is 'GBR123'. 
- Log in with admin email and password and copy access token
- Enter access token in the authorization header as bearer
- Proceed to test out admin functions ie create new students, create new courses, delete students etc
- Log in as a student (note: use a valid email address to create the student account to enable you recieve the login password sent by the admin)
- Test out student functions ie register courses, etc

......


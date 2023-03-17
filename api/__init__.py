from flask import Flask
from flask_restx import Api
from .db import db
from .config.config import config_dict
from .auth.views import auth_namespace
from .students.views import  students_namespace
from .admin.views import  admin_namespace
from .models.students import Student
from .models.courses import Course, StudentCourse, Score
from .models.users import User, Admin
from flask_migrate import Migrate 
from pathlib import Path 
from .utils.blacklist import BLACKLIST
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed

def create_app(config=config_dict['dev']):
    
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLACKLIST

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; ** token to authorize"
        }
    }


    api = Api(
        app,
        title='Student Management System API',
        description='A student management system REST API service',
        authorizations=authorizations, 
        security='Bearer Auth'
        )


    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(students_namespace, path='/students')
    api.add_namespace(admin_namespace, path='/admin')

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 404

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Score': Score,
            'Admin': Admin,
            'Student': Student,
            'StudentCourse': StudentCourse,
            'Course': Course,
        }

    return app
from flask_restx import fields
from http import HTTPStatus
from datetime import datetime
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, get_jwt_identity , get_jwt,
    create_refresh_token
)
from werkzeug.security import (
    check_password_hash , 
    generate_password_hash
)
from flask import  request 
from flask_restx import Namespace, Resource
from ..models.students import Student
from ..models.users import User, Admin
from ..utils import admin_required, random_char, MailServices
from ..db import db
from ..utils.blacklist import BLACKLIST

mail = MailServices()



login_fields_serializer = {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
}


register_fields_serializer = {
    'email': fields.String(required=True, description='User email address'),
    'first_name': fields.String(required=True, description="First name"),
    'last_name': fields.String(required=True, description="Last name"),
    'password': fields.String(required=True, description="A password"),
    'reg_code': fields.String(required=True, description="A code to determine user type")
}

register_student_fields_serializer = {
    'email': fields.String(required=True, description='User email address'),
    'first_name': fields.String(required=True, description="First name"),
    'last_name': fields.String(required=True, description="Last name"),
}

auth_namespace = Namespace('auth', description='Namespace for Authentication')

login_serializer = auth_namespace.model('Login serializer', login_fields_serializer)
register_serializer = auth_namespace.model('Register serializer', register_fields_serializer)
register_student_serializer = auth_namespace.model('Register Student serializer', register_student_fields_serializer)




# Route for registering a user 
@auth_namespace.route('/register')
class AdminRegistrationView(Resource):

    @auth_namespace.expect(register_serializer)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible to only admins. 
            It allows creation of admin accounts with the special registration code.
            """
    )
    def post(self):
        """ Create a new admin account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'User already exists'} , HTTPStatus.CONFLICT
        # Create new admin
        
        if data.get('reg_code') == "GBR123":
            new_user =  Admin (
                email=data.get('email'), 
                name=f"{data.get('first_name')} {data.get('last_name')}",
                user_type='admin',
                password_hash=generate_password_hash(data.get('password')),
                reg_code=data.get('reg_code')
            )
            try:
                new_user.save()
            except:
                db.session.rollback()
                return {'message': 'An error occurred while saving admin'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED
        else:
            return {'message': 'Incorrect Admin registration code!'}





# Route for Token refresh 
@auth_namespace.route('/login/refresh')
class Refresh(Resource):
    @auth_namespace.doc(
        description="""
            This endpoint is accessible to all users. 
            It allows user refresh their tokens
            """
    )
    @jwt_required(refresh=True)
    def post(self):
        """
            Generate new tokens
        """
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,

            }, HTTPStatus.OK


# Route for user login( Authentication )
@auth_namespace.route('/login')
class UserLoginView(Resource):
    @auth_namespace.expect(login_serializer)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible to all users. 
            It allows user authentication
            """
    )
    def post(self):
        """ Authenticate a user"""
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            response = {'message': 'Invalid username or password'}
            return response, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token, 
            }
        return response, HTTPStatus.OK


@auth_namespace.route('/logout')
class Logout(Resource):
    @jwt_required(verify_type=False)
    def post(self):
        """
        Revoke Access/Refresh Token
        """
        token = get_jwt()
        jti = token["jti"]
        token_type = token["type"]
        BLACKLIST.add(jti)
        return {"message": f"{token_type.capitalize()} token successfully revoked"}, HTTPStatus.OK
    


# route for an admin to create a student
@auth_namespace.route('/register/student')
class StudentRegistrationView(Resource):

    @auth_namespace.expect(register_student_serializer)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible to admins only 
            It allows the admin to create a student account
            """
    )
    @admin_required()
    def post(self):
        """ Create a new student account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'User already exists'} , HTTPStatus.CONFLICT
        
        current_year =  str(datetime.now().year)
        a = 1
        reg_no= f"{current_year}/STD{a}"
        password = random_char(10)
        
        new_user =  Student(
            email=data.get('email'), 
            reg_no=reg_no,
            name=f"{data.get('first_name')} {data.get('last_name')}",
            user_type='student',
            password_hash=generate_password_hash(password),
        )
        a = new_user.id
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED, mail.student_details_mail(new_user.email, data.get('first_name'), new_user.reg_no, password)










from ..utils import admin_required, student_required, convert_grade_to_gpa
from ..db import db
from flask import request
from ..models.courses import Student, StudentCourse , Course , Score
from ..models.users import User 
from flask_jwt_extended import  get_jwt_identity  
from flask_restx import Namespace, Resource
from .serializers import (
    students_fields_serializer , 
    course_fields_serializer,
    course_retrieve_fields_serializer
)
from http import HTTPStatus


students_namespace = Namespace('students', description='Namespace for Student ')



students_serializer = students_namespace.model('Student list', students_fields_serializer)
courses_serializer = students_namespace.model('Student and course list', course_retrieve_fields_serializer)
courses_add_serializer = students_namespace.model('Add courses', course_fields_serializer)


@students_namespace.route('/courses')
class StudentCoursesListView(Resource):

    @students_namespace.marshal_with(courses_serializer)
    @student_required()
    def get(self, student_id):
        """
        Retrieve a student courses
        """  
        authenticated_student_id = get_jwt_identity()   
        courses = StudentCourse.get_student_courses(id=authenticated_student_id)
        return courses , HTTPStatus.OK


@students_namespace.route('/courses/add_and_drop')
class StudentCourseRegisterView(Resource):

    @students_namespace.marshal_with(courses_serializer)
    @students_namespace.expect(courses_add_serializer)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to a student. 
            It allows a student register for a course
            """
    )
    @student_required()  
    def post(self):
        """ 
        Register for a course 
        """     
        authenticated_user_id = get_jwt_identity() 
        student = Student.query.filter_by(id=authenticated_user_id).first()   
        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()  
        if course:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                return {
                    'message':'Course has already been registered'
                    } , HTTPStatus.OK
            # Register the student to the course
            add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
            try:
                add_student_to_course.save()
                return {'message': 'Course registered successfully'} , HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while registering course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND


    @students_namespace.expect(courses_add_serializer)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to a student. 
            It allows a student unregister for a course
            """
    )
    @student_required()
    def delete(self):
        """
        Unregister a  course
        """
        data = request.get_json()
        authenticated_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=authenticated_user_id).first()   
        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()  
        if course:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                try:
                    get_student_in_course.delete()
                    return {'message': 'Course deleted successfully'} , HTTPStatus.NO_CONTENT
                except:
                    db.session.rollback()
                    return {'message': 'An error occurred while deleting this course'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {
                    'message':'You did not register for this course'
                    } , HTTPStatus.BAD_REQUEST

        return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND
    
    
@students_namespace.route('/courses/grade')
class CoursesGradeListView(Resource):

    @students_namespace.doc(
        description="""
            This endpoint is accessible to students. 
            It allows a student retrieve all registered courses grade
            """
    )
    @student_required()
    def get(self):
        """
        Retrieve all student courses grade
        """     
        authenticated_user_id = get_jwt_identity() 
        student = Student.query.filter_by(id=authenticated_user_id).first()  
        courses = StudentCourse.get_student_courses(student.id)
        response = []
        
        for course in courses:
            grade_response = {}
            score_in_course = Score.query.filter_by(student_id=student.id , course_id=course.id).first()
            grade_response['name'] = course.name
            if score_in_course:
                grade_response['score'] = score_in_course.score
                grade_response['grade'] = score_in_course.grade
            else:
                grade_response['score'] = None
                grade_response['grade'] = None 
            response.append(grade_response)
        return response , HTTPStatus.OK    

     
@students_namespace.route('/gpa')
class StudentGPAView(Resource):


    @student_required()
    def get(self):
        """
        Calculate a student gpa score
        """    
        authenticated_student_id = get_jwt_identity()
        student = Student.get_by_id(id=authenticated_student_id)
        # get all the course the students offer
        courses = StudentCourse.get_student_courses(student.id)
        total_weighted_gpa = 0
        total_unit_load = 0
        for course in courses:
            # check if student have a score for the course
            score_exist = Score.query.filter_by(student_id=student.id, course_id=course.id).first()
            if score_exist:
                grade = score_exist.grade
                # calculate the gpa for the course
                gpa = convert_grade_to_gpa(grade)
                weighted_gpa = gpa * course.unit_load
                total_weighted_gpa += weighted_gpa
                total_unit_load += course.unit_load
        if total_unit_load == 0:
            return {
                'message':'GPA calculation completed.',
                'gpa': total_unit_load
            }, HTTPStatus.OK
        else:
            gpa =  total_weighted_gpa / total_unit_load
            return {
                'message':'GPA calculation completed',
                'gpa': round(gpa , 2 ) 
            }, HTTPStatus.OK




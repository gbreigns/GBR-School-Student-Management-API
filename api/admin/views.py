from ..models.courses import ( Student, Course, StudentCourse , Score )
from ..db import db
from ..utils import admin_required, get_grade
from ..students.serializers import students_fields_serializer, course_retrieve_fields_serializer, student_score_add_fields_serializer
from flask_restx import Namespace, Resource , fields
from http import HTTPStatus
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity


admin_namespace = Namespace('admin', description='Namespace for admin functions')

course_creation_serializer = admin_namespace.model(
    'Course creation serializer', {
        'name': fields.String(required=True, description="Course name"),
        'course_code': fields.String(required=True, description="Course code"),
        'unit_load': fields.Integer(description="Course unit load"),
        'teacher_first_name': fields.String(required=True, description="Course teacher firstname"),
        'teacher_last_name': fields.String(required=True, description="Course teacher lastname"),
    }
)

student_course_register_serializer = admin_namespace.model(
    'Student Course Creation Serializer', {
        'student_id': fields.String(required=True, description="A student id"),
    }
)
 
students_serializer = admin_namespace.model( 'Student Serializer', students_fields_serializer)
student_score_add_serializer = admin_namespace.model( 'Add student score', student_score_add_fields_serializer)

course_retrieve_serializer = admin_namespace.model('Course Retrieval serializer', course_retrieve_fields_serializer)


@admin_namespace.route('/courses')
class CoursesListView(Resource):

    @admin_namespace.marshal_with(course_retrieve_serializer)
    @admin_namespace.doc(
        description="""
            This endpoint is accessible to all users. 
            It allows the retrieval of all available courses
            """
    )
    @jwt_required()
    def get(self):
        """
        Retrieve all available courses
        """
        courses = Course.query.all()
        return courses , HTTPStatus.OK
    

    @admin_namespace.expect(course_creation_serializer) 
    @admin_namespace.doc(
        description="""
            This endpoint is accessible to an admin. 
            It allows admin create a new course
            """
    )
    @admin_required()
    def post(self):
        """
        Create a new course
        """
        data = request.get_json()
        new_course = Course (
            name=data.get('name'),
            course_code=data.get('course_code'),
            unit_load=data.get('unit_load'),
            teacher_name=f"{data.get('teacher_first_name')} {data.get('teacher_last_name')}",
        )
        
        
        try:
            new_course.save()
            return {'message': 'Course created successfully'}, HTTPStatus.CREATED
        except:
            return {'message': 'An error occurred while saving course'}, HTTPStatus.INTERNAL_SERVER_ERROR



@admin_namespace.route('/course<int:course_id>')
class CourseRetrievalView(Resource):

    @admin_namespace.marshal_with(course_retrieve_serializer)
    def get(self, course_id ):
        """
        Retrieve a course
        """
        course = Course.get_by_id(course_id)
        return course , HTTPStatus.OK
    
    @admin_namespace.doc(
        description="""
            This endpoint is accessible to an admin. 
            It allows admin delete a course
            """
    )
    @admin_required()
    def delete(self, course_id):
        """
        Delete a course
        """
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return {'message':'Course does not exist'}, HTTPStatus.NOT_FOUND
        try:
            course.delete()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while deleting course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return HTTPStatus.NO_CONTENT
    



@admin_namespace.route('/course<int:course_id>/students/add_and_drop')
class CourseRetrievalView(Resource):


    @admin_namespace.expect(student_course_register_serializer)
    @admin_namespace.doc(
        description="""
            This endpoint is accessible to admin only. 
            It allows admin add a  student to any course
            """
    )
    @admin_required()
    def post(self, course_id ):
        """
        Register a student to a course
        """
        data = request.get_json()
        student_id = data.get('student_id')
        # check if student and course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(course_id).first()
        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND
        if student:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                return {
                    'message':'{} has already registered for the course'.format(student.name)
                    } , HTTPStatus.OK
            # Register the student to the course
            add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
            try:
                add_student_to_course.save()
                return {'message': 'Course registered successfully'} , HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while registering course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Student does not exist'} , HTTPStatus.NOT_FOUND
    


    @admin_namespace.doc(
        description="""
            This endpoint is accessible to admins. 
            It allows an admin remove a student from any course
            """
    )
    @admin_required()
    def delete(self, course_id):
        """
        Unregister a student course
        """
        data = request.get_json()
        student_id = data.get('student_id')
        # check if student and course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(course_id).first()
        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND
        if student:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                try:
                    get_student_in_course.delete()
                    return {'message': 'Course deleted successfully'} , HTTPStatus.NO_CONTENT
                except:
                    db.session.rollback()
                    return {'message': 'An error occurred while deleting student course'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {
                    'message':'{} has not register for this course'.format(student.name)
                    } , HTTPStatus.BAD_REQUEST
    


@admin_namespace.route('/course<int:course_id>/students')
class CourseStudentsListView(Resource):

    @admin_namespace.marshal_with(students_serializer) 
    @admin_namespace.doc(
        description="""
            This endpoint is accessible to admins. 
            It allows the retrieval of all students in a course
            """
    )
    @admin_required()
    def get(self, course_id ):
        """
        Retrieve all registered student in a course
        """
        course = Course.get_by_id(course_id)
        get_student_in_course = StudentCourse.get_students_in_course_by(course.id) 
        return get_student_in_course , HTTPStatus.OK

# Route for admin to retrieve all registered students
@admin_namespace.route('/All_Students')
class StudentsListView(Resource):

    @admin_namespace.marshal_with(students_serializer)
    @admin_namespace.doc(
        description="""
            This endpoint is accessible only to an admin user. 
            It allows the admin retrieve all students(registered) in the school
            """
    )
    @admin_required() 
    def get(self):
        """
        Retrieve all students in school
        """
        students = Student.query.all()
        return students , HTTPStatus.OK


@admin_namespace.route('/student<int:student_id>')
class StudentRetrieveDeleteUpdateView(Resource):

    @admin_namespace.marshal_with(students_serializer)
    @admin_namespace.doc(
        description="""
            This endpoint is accessible only to an admin 
            It allows the  retrieval of a particular student
            """
    )
    @admin_required()
    def get(self, student_id):
        """
        Retrieve a student 
        """
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return {'message':'Student does not exist'}, HTTPStatus.NOT_FOUND
        return student , HTTPStatus.OK
    
    @admin_required()
    def delete(self, student_id):
        """
        Remove a student 
        """
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return {'message':'Student does not exist'}, HTTPStatus.NOT_FOUND
        try:
            student.delete()
            return {'message': 'Student removed successfully'} , HTTPStatus.NO_CONTENT
        except:
            db.session.rollback()
            return {'message': 'An error occurred while removing this student'}, HTTPStatus.INTERNAL_SERVER_ERROR


@admin_namespace.route('/student/course/add_score')
class StudentCourseScoreAddView(Resource):

    @admin_namespace.expect(student_score_add_serializer)
    @admin_namespace.doc(
        description='''
            This endpoint is accessible only to an admin. 
            It allows an admin add a student's score in a course.
            '''
    )
    @admin_required()
    def put(self):
        """
        Add a student course score
        """     
        authenticated_user_id = get_jwt_identity()
        student_id = request.json['student_id']
        course_id = request.json['course_id']
        score_value = request.json['score']   
        # check if student and course exist
        student = Student.query.filter_by(id = student_id).first()
        course = Course.query.filter_by(id=course_id).first()
        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND
        # check if student is registered for the course
        student_in_course = StudentCourse.query.filter_by(course_id=course.id, student_id=student.id).first() 
        if student_in_course:
            # check if the student already have a score in the course
            score = Score.query.filter_by(student_id=student_id, course_id=course_id).first()
            grade = get_grade(score_value)
            if score:
                score.score = score_value
                score.grade = grade
            else:
                # create a new score object and save to database
                score = Score(student_id=student_id, course_id=course_id, score=score_value , grade=grade)
            try:
                score.save()
                return {'message': 'Score added successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while saving student course score'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'The student is not registered for this course'}, HTTPStatus.BAD_REQUEST
    

admin_namespace.route('/student<int:student_id>/courses/grade')
class StudentCoursesGradeListView(Resource):

    @admin_required()
    def get(self, student_id):
        """
        Retrieve a student all courses grade
        """     
        courses = StudentCourse.get_student_courses(student_id)
        response = []
        
        for course in courses:
            grade_response = {}
            score_in_course = Score.query.filter_by(student_id=student_id , course_id=course.id).first()
            grade_response['name'] = course.name
            if score_in_course:
                grade_response['score'] = score_in_course.score
                grade_response['grade'] = score_in_course.grade
            else:
                grade_response['score'] = None
                grade_response['grade'] = None 
            response.append(grade_response)
        return response , HTTPStatus.OK
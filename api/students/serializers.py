from flask_restx import fields



students_fields_serializer = {
    'id': fields.String(),
    'email': fields.String(required=True, description='User email address'),
    'name': fields.String(required=True, description="full name"),
    'reg_no': fields.String(required=True, description="student registration number"),
}



student_score_add_fields_serializer = {
    'student_id': fields.Integer(required=False, description='ID of student'),
    'course_id': fields.Integer(required=True, description='ID of course'),
    'score': fields.Integer(required=True, description="Score value"),
}



course_fields_serializer = {
    'course_id': fields.String(required=True),
}

course_retrieve_fields_serializer =  {
    'id': fields.Integer(),
    'name': fields.String(required=True, description="A course name"),
    'course_code': fields.String(description="A course code")
}
from ..db import db
from .students import Student

# Model for adding/storing courses
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    course_code = db.Column(db.String(10), unique=True)
    unit_load = db.Column(db.Integer, default=1) 
    teacher_name = db.Column(db.String(50))
   

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)


# Model for storing students and their registered courses
class StudentCourse(db.Model):
    __tablename__ = 'student_course'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    # returns students registered for a particular course
    @classmethod
    def get_students_in_course_by(cls, course_id):
        students = (
            Student.query.join(StudentCourse)
            .join(Course).filter(Course.id == course_id).all()
        )
        return students
    
    # returns registered courses for a particular student
    @classmethod
    def get_student_courses(cls, student_id):
        courses = (
            Course.query.join(StudentCourse)
            .join(Student).filter(Student.id == student_id).all()
        )
        return courses
    

# model for uploading/storing student scores
class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    score = db.Column(db.Float , nullable=False)
    grade = db.Column(db.String(5) , nullable=True )
    

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

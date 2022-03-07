from flask import Flask

from utils import *
from skydb.classes import *
from skydb.sheets import updateSpreadsheet
from skydb.update import updateTable

from google.cloud import storage

app = Flask(__name__)

# Loading the api token
storage_client = storage.Client()
bucket = storage_client.bucket('sky-api-326214.appspot.com')
BLOB = bucket.blob('.sky-token')
BLOB.download_to_filename('/tmp/.sky-token')


@app.route('/')
def main():
    return "Hello Friend"

@app.route('/users')
def updateUsers():
    pairs = {
        "Student":{
            'class':Student,
            'function':getStudents,
            'table_type':'Normal'
        },
        "Teacher":{
            'class':Teacher,
            'function':getTeachers,
            'table_type':'Normal'
        }
    }
    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            data_function = table.get('function'), 
            table_type=table['table_type']
            )

    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello Users"

@app.route('/grades')
def updateGradebookGrades():
    updateTable(db_class=GradebookGrades, data_function=getRawGrades, table_type="Grades")
    BLOB.upload_from_filename('/tmp/.sky-token')
    return 'Hello New Grades'
    
@app.route('/testscores')
def updateTestScores():
    updateTable(db_class=Psat, data_function=getPsatScores, table_type='User')
    BLOB.upload_from_filename('/tmp/.sky-token')
    return 'Hello New PSAT Scores'

@app.route('/officalrecords')
def updateOfficalRecords():
    offical_records = getOfficialRecords()
    pairs = {
        "GPAS":{
            'class': GPA,
            'data':offical_records['gpas'],
            'table_type':'User'
        },
        'Grades':{
            'class':HistoricGrades,
            'data':offical_records['grades'],
            'table_type':'HistoricGrades'
        }
    }

    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            table_type=table['table_type']
            )

    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello new Student Record Data"

@app.route('/courses')
def updateCourses():
    pairs = {
        "Course":{
            'class':Course,
            'function':getCourses,
            'table_type':'Normal'
        },
        'Section':{
            'class':Section,
            'function':getSections,
            'table_type':'Normal'
        },
        'advisingSections':{
            'class':AdvisingSection,
            'function':getAdvisingSections,
            'table_type':'Normal'
        }
    }

    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            data_function = table.get('function'), 
            table_type=table['table_type']
            )

    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello new Course data"

@app.route('/enrollment')
def updateEnrolllment():
    enrollment = eatSeafoodMedley()

    academic_enrollments = enrollment['academic_enrollments']
    advisory_enrollments = enrollment['advisory_enrollments']
    athletic_enrollments = enrollment['athletic_enrollments']
    
    pairs = {
        'academicEnrollment':{
            'class':AcademicEnrollment,
            'data':academic_enrollments,
            'table_type':'Enrollment'
        },
        'academicEnrollment':{
            'class':AdvisoryEnrollment,
            'data':advisory_enrollments,
            'table_type':'Enrollment'
        },
        'academicEnrollment':{
            'class':AthleticEnrollment,
            'data':athletic_enrollments,
            'table_type':'Enrollment'
        }
    }

    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            data_function = table.get('function'), 
            table_type=table['table_type']
            )
    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello New Enrollment Data"

@app.route('/attendance')
def updateAttendance():
    pairs = {
        'Attendance':{
            'class':Attendance,
            'function':getAttendance,
            'table_type':'Normal'
        },
        'AttendanceCodes':{
            'class':AttendanceCode,
            'function':getAttendanceCodes,
            'table_type':'attendance_codes'
        },
    }

    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            data_function = table.get('function'), 
            table_type=table['table_type']
            )
    
    return "Hello New Attendance Data"

@app.route('/admissions')
def updateAdmissions():
    pairs = {
        'Candidate':{
            'class':Candidate,
            'function':getCandidates,
            'table_type':'Normal'
        },
        'contracts':{
            'class':Contract,
            'function':getContracts,
            'table_type':'Contracts'
        },
    }

    for table in pairs.values():
        updateTable(
            db_class = table['class'], 
            data = table.get('data'), 
            data_function = table.get('function'), 
            table_type=table['table_type']
            )

    # Saving the token to Google Cloud Storage
    BLOB.upload_from_filename('/tmp/.sky-token')

    return "Hello New Admissions Data"

@app.route('/legacy')
def updateSpreadSheets():
    grades = legacyGradeReport()
    absences = getAbsences().reset_index()
    updateSpreadsheet(grades.astype(str), sheet_name = "Sky Grades")
    updateSpreadsheet(absences.astype(str), sheet_name="Sky Attendance")
    # Saving the token to Google Cloud Storage
    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello new spreadsheet data"

@app.route('/ms2-grades')
def updateSemesterGrades():
    ms2 = getSemesterGrades('ms2')
    updateSpreadsheet(ms2, 
                    sheet_id='1kE8btksO6e0wUs_ep_YjwrP3pXsWrNgsHyhvkowuXEQ', 
                    styleClass=HysonFireStyle,
                    )
    # Saving the token to Google Cloud Storage
    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello new ms2 spreadsheet data"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
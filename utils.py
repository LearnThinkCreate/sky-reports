import time

from academics import getAdvisingSections, getCourses, getEnrollments, getSections, eatSeafoodMedley
from admissions import getCandidates, getContracts
from attendance import getAbsences, getAttendance, legacyAttendance, getAttendanceCodes
from config import sky
from skydb.connections import GooglePsqlConnection
# from course_request import 
from google_sheets import HysonFireStyle
from grades import getRawGrades, legacyGradeReport, getSemesterOneGrades
from records import getOfficialRecords, getPsatScores
from users import getAdvisors, getStudents, getTeachers

def timeFunction(func,  *args, **kwargs):
    start = time.time()
    func(*args, **kwargs)
    end=time.time()
    return (end - start)


def stringToComparison(comparison_string):
    return (comparison_string or '') + "%"


def calldb(stmt, request_type="all"):
    conn = GooglePsqlConnection().getconn()
    cur = conn.cursor()
    cur.execute(stmt)
    if request_type == "single":
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    return result








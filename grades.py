import os
import pandas as pd

from config import sky
from users import getAdvisors
from academics import getEnrollments

def getRawGrades(current=True):
    raw_grades = sky.getAdvancedList(os.environ.get('SID_RG'))
    if not current:
        return raw_grades
    # Filtering for the current acadmeic turn
    grades = raw_grades[raw_grades.term.isin(sky.getTerm(active=True))].reset_index(drop=True)
    grades.last_updated = pd.to_datetime(grades.last_updated)
    return grades

def getGradebookGrades():  
    # Getting advisors
    advisors = getAdvisors()
    
    # Getting the grades
    grades = getRawGrades()

    # Student Enrollments
    enrollment = getEnrollments()

    # Getting student grade levels by calling the sky api
    full_grades = enrollment.merge(advisors).merge(grades, on=['user_id', 'section_id'], how='left')
    
    # Sorting data
    full_grades = full_grades.sort_values(['lastname', 'firstname', 'block'])

    # Adding full name column to data
    full_grades['full_name'] = full_grades['lastname'] + ", " + full_grades['firstname']
    
    # Being a good boy
    full_grades.fillna(0, inplace = True)
    full_grades.reset_index(inplace = True, drop = True)
    
    return full_grades

def getSemesterOneGrades():

    # Pulling the data from Blackbaud Advanced List
    grades = sky.getAdvancedList(os.environ.get('SID_S1G'))[['user_id', 'course_code', 'grade', 'grade_plan',]]
    comments = sky.getAdvancedList(os.environ.get('SID_S1C'))[['user_id', 'course_code', 'comment']]
    enrollments = getEnrollments(False)
    # Pulling the students level descriptions
    students = sky.getAdvancedList(os.environ.get('SID_ST'))[ ['user_id', 'level_description', 'grade_level', 'advisor_id']]
    # Pulling advisors for Tableau sorting
    advisors = getAdvisors()
    advisors.Section = advisors.Section.str.replace(' ', '')

    # Filtering the RC data for Semester 1 grades
    reportcardGrades = grades.merge(
            comments,
            'left'
        )

    # Getting the enrollments for the fall term
    currentEnrollment = enrollments[enrollments.term_name == 'Fall Semester']

    # Getting Enrollment for the current term
    # currentEnrollment = enrollments[enrollments.term_name == sky.getTerm(active=True).values[0]]

    # Adding the Semester 1 grades to the current Enrollments
    semesterGrades = currentEnrollment.merge(
            reportcardGrades, 
            'left', 
            on=['user_id','course_code']
        ).drop_duplicates()

    # Joining data
    fullSemesterGrades = semesterGrades.merge(students, 'inner').merge(advisors, 'inner')

    # Cleaning the data for the google spreadsheet
    fullSemesterGrades.fillna("", inplace = True)
    fullSemesterGrades.reset_index(inplace = True, drop = True)
    fullSemesterGrades.drop_duplicates(inplace=True)

    return fullSemesterGrades


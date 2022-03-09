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

 
def getSemesterGrades(semester="S1", report=False):

    # Getting student Enrollment
    enrollments = getEnrollments(False)

    # Pulling the students level descriptions
    students = sky.getAdvancedList(os.environ.get('SID_ST'))[ ['user_id', 'level_description', 'grade_level', 'advisor_id', 'first_name', 'last_name']]
   
    # Pulling advisors for Tableau sorting
    advisors = getAdvisors()
    advisors.Section = advisors.Section.str.replace(' ', '')

    # Pulling the data from Blackbaud Advanced List
    if semester == "S1":
        # Pulling s1 grades & comments
        grades = sky.getAdvancedList(os.environ.get('SID_S1G'))[['user_id', 'section_id', 'grade', 'grade_plan',]]
        comments = sky.getAdvancedList(os.environ.get('SID_S1C'))[['user_id', 'section_id', 'comment']]
        
        # Getting the enrollments for the fall term
        currentEnrollment = enrollments[enrollments.term_name == 'Fall Semester']
    elif semester == "MS2":
        # Pulling s1 grades & comments
        grades = sky.getAdvancedList(74335)[['user_id', 'section_id', 'grade', 'grade_plan',]]
        comments = sky.getAdvancedList(74336)[['user_id', 'section_id', 'comment']]
        
        # Getting the enrollments for the fall term
        currentEnrollment = enrollments[enrollments.term_name == 'Spring Semester']   

    # Filtering the RC data for Semester 1 grades
    reportcardGrades = grades.merge(
            comments,
            'left'
        )

    # Adding the Semester 1 grades to the current Enrollments
    semesterGrades = currentEnrollment.merge(
            reportcardGrades, 
            'left', 
            on=['user_id','section_id']
        ).drop_duplicates()

    # Joining data
    fullSemesterGrades = semesterGrades.merge(students, 'inner').merge(advisors, 'inner')

    # Cleaning the data for the google spreadsheet
    fullSemesterGrades.fillna("", inplace = True)
    fullSemesterGrades.reset_index(inplace = True, drop = True)
    fullSemesterGrades.drop_duplicates(inplace=True)

    fullSemesterGrades =(fullSemesterGrades[[
        'first_name', 'last_name', 'grade_level', 'section_id', 'grade', 
        'grade_plan',  'course_code', 'course_title', 'department_name',
        'teacher_last', 'term_name', 'comment', 'level_description',
        'Section', 'advisor_first', 'advisor_last', 'user_id', 'block'
        ]]
        .rename(columns={
            'term_name':'term',
            'teacher_last':'Teacher'
            })
        .astype({'section_id':'int64'})
    )

    if report:
        slim_grades = fullSemesterGrades.sort_values(['grade_level', 'last_name', 'first_name', 'block'])
        slim_grades = (
            slim_grades
            .assign(Student=lambda x: x['last_name'] + ', ' + x['first_name'])
            .rename(columns={
                'advisor_last':'Advisor',
                'course_title':'Course',
                'grade':"Grade"
            })
            [[
                'Student', 'Advisor', 'Course',
                'Teacher', 'Grade', 'level_description', 'grade_level', 
                'user_id'
            ]]
            )
        return slim_grades
    return fullSemesterGrades.sort_values('user_id')


def legacyGradeReport():
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

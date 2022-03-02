import re
import os
import pandas as pd

from config import sky

def getTeachers():
    teachers = sky.getUsers(['Teacher', 'Advisor'])
    teachers = teachers[['id', 'first_name', 'last_name', 'gender', 'email']]
    teachers = teachers.drop_duplicates().reset_index(drop=True)
    return teachers

def getStudents():
    students = sky.getUsers()

    clean_students = students[[
        'id', 'student_id', 'first_name', 'last_name',
        'preferred_name', 'student_info.grade_level',
        'custom_field_one', 
    ]].rename(columns={
        'student_info.grade_level':'grade_level',
        'custom_field_one':'counselor',
    }).astype({
        'id':'int64',
        'grade_level':'int32'
    })

    clean_students.student_id = pd.to_numeric(clean_students.student_id, errors='coerce')

    clean_students = clean_students.astype(object).where(pd.notnull(clean_students), None)

    return clean_students

def getAdvisors():
    # Pulling advisory information
    advisors = sky.getAdvancedList(os.environ.get('SID_AD'))

    advisors = advisors[[
        'advisor_id', 'advisor_first', 'advisor_last',
        'advisor_email', 'advisoryTitle', 'user_id'
    ]]

    advisors['Section'] = None
    for index, row in advisors.iterrows():
        # Title of the advising section 
        value = row['advisoryTitle']
        # Finding the grade level
        match = re.search('[\\d].', value)
        gradeLevel = int(match.group())
        # Finding the teachers name
        name = re.search('(?<=[\\d].).*', value)
        name = name.group().strip()

        row['Section'] = f'{name} {gradeLevel}'

    advisors.drop('advisoryTitle', axis=1, inplace=True)
    
    return advisors
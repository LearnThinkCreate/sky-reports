import os 
import re

import pandas as pd
from config import sky


def eatSeafoodMedley():
    # Getting enrollments from sky API
    enrollments = sky.enrollmentMedley()

    # Cleaning the academic enrollments 
    enrollments['academics'].section_id = enrollments['academics'].section_id.astype('int64')
    academic_enrollments = enrollments['academics']
    academic_enrollments = academic_enrollments[[
        'user_id', 'section_id', 'block_name', 'course_title',
        'duration_name', 'department_name', 'faculty_first_name',
        'faculty_last_name'
    ]].rename(columns={
        'block_name':'period',
        'duration_name':'term',
        'department_name':'department',
        'faculty_first_name':"teacher_first",
        'faculty_last_name':'teacher_last'
    })

    # Cleaning advisory enrollments
    enrollments['advisory'].section_id = enrollments['advisory'].section_id.astype('int64')
    advisory_enrollments = enrollments['advisory']
    advisory_enrollments = advisory_enrollments[['user_id', 'section_id']]

    # Cleaning athletic enrollments
    enrollments['athletics'].section_id = enrollments['athletics'].section_id.astype('int64')
    athletic_enrollments = enrollments['athletics']
    athletic_enrollments = athletic_enrollments.rename(columns={
        'course_title':'sport',
        'faculty_first_name':'coach_first',
        'faculty_last_name':'coach_last',
        'duration_name':'season'
    })

    return {
        "academic_enrollments":academic_enrollments,
        "advisory_enrollments":advisory_enrollments,
        "athletic_enrollments":athletic_enrollments
    }

def getCourses():
    # Getting levels for merge with courses
    levels = sky.getLevels()
    levels = levels.rename(columns={'id':'level_num', 'name':'level_description'})
    # Getting courses from BB
    courses = sky.get('academics/courses')
    # Cleaning data 
    courses = courses.merge(levels)
    courses = courses[[
        'offering_id', 'course_code', 'course_title',
        'level_description', 'course_length', 'inactive'
    ]].astype({'inactive':"bool"}).rename(columns={'offering_id':'id'})

    return courses

def getSections():
    # Get sections from sky API
    sections = sky.getSections()
    # Cleaning df
    sections = sections[[
            'id', 'offering_id', 'duration.name', 'teacher.id'
        ]].rename(columns={
            'duration.name':"term",
            "teacher.id":"teacher_id"
        }).astype({
            'id':'int64', 'teacher_id':"int64", 'offering_id':'int64'
            })

    return sections.drop_duplicates().reset_index(drop=True)

def getAdvisingSections():
    # Getting the school levels
    levels = sky.getLevels()
    # Initalizing df
    data = pd.DataFrame()
    for level in levels.id.tolist():
        # Getting adv sections for each level
        df = sky.get('advisories/sections', params={'level_num':level})
        data = pd.concat([data, df], ignore_index=True)
    
    # Cleaning the advisor data
    data.dropna(axis=0, subset=['id'], inplace=True)
    advisors = data.advisors.explode().apply(pd.Series).astype({
            'head':'bool'
        }).rename(columns={
            'head':'head_teacher', 
            'id':'advisor_id',
            'name':'advisor_name'
        })
    # Getting Head Teachers
    advisors = advisors.loc[advisors.head_teacher].drop('head_teacher', axis=1)
    # Droping advisors list col
    data.drop('advisors', axis=1, inplace=True)
    # Merging section and advisor data
    advising_section = data.merge(advisors, left_index=True, right_index=True)
    # Cleaning the advising title 
    advising_section.name = advising_section.name.str.split(' - ').str[0]
    advising_section['title'] = None
    for index, row in advising_section.iterrows():
        # Title of the advising section 
        value = row['name']
        # Finding the grade level
        match = re.search('[\\d].', value)
        gradeLevel = int(match.group())
        # Finding the teachers name
        name = re.search('(?<=[\\d].).*', value)
        name = name.group().strip()

        advising_section.loc[index, 'title'] = f'{name}{gradeLevel}'
        advising_section = advising_section.astype({'id':'int64'})[[
            'id', 'title', 'course_code', 'school_year',
            'duration.name', 'advisor_id', 'advisor_name'
        ]]

    advising_section = advising_section[[
        'id', 'advisor_id', 'title', 
        'course_code', 'duration.name', 'advisor_name'
    ]].rename(columns={'duration.name':'term'})

    return advising_section


def getEnrollments(current=True):
    raw_enrollment = sky.getAdvancedList(73530)
    if not current:
        return raw_enrollment
    # Filtering for the current academic term
    enrollment = raw_enrollment[raw_enrollment.term_name.isin(sky.getTerm(active=True))].reset_index(drop=True)
    return enrollment
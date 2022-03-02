import os
import pandas as pd 

from config import sky
from skydb.sheets import readSpreadsheet

def getOfficialRecords():
    TRANSCRIPT_GRADES = os.environ.get('SID_TRANSFER')
    TRANSCRIPT_TRANSFER_GRADES = os.environ.get('SID_TRANSCRIPT')

    transcript_grades = sky.getAdvancedList(TRANSCRIPT_GRADES)
    transcript_transfer_grades = sky.getAdvancedList(TRANSCRIPT_TRANSFER_GRADES)

    """ Adding GPA Points from offical transcript grades """
    gpa_points = (transcript_grades[['gpa_points', 'grade']]
    .drop_duplicates()
    .dropna()
    )

    transcript_transfer_grades = (
        transcript_transfer_grades
        .merge(
            gpa_points,
            'inner',
            on='grade'
        )
    )

    """ Combining row data from the two dfs """
    student_records = (
        pd.concat(
        [transcript_grades[list(transcript_grades.columns)], 
        transcript_transfer_grades[list(transcript_transfer_grades.columns)]],
        axis=0
        )
        .sort_values(['last_name', 'first_name', 'user_id', 'school_year', 'term'])
        .query("level_description == 'Upper School'")
        .reset_index(drop=True)
        .astype({
            'user_id':'int64',
            'credits_attempted':'float',
            'credits_earned':'float',
            'offering_id':'int64',
            'gpa_points':'float',
            'weight':'float'
        })
    )

    """ Filtering out any MS Students """
    students = sky.getUsers()

    highschoolers = (
        students[['id', 'student_info.grade_level_abbreviation']]
        .astype('int64')
        .rename(columns={
        'id':'user_id',
        'student_info.grade_level_abbreviation':'grade_level'
        })
        .query("grade_level > 8")
        .drop('grade_level', axis=1)
        .user_id
        .tolist()
    )

    student_records = student_records[student_records.user_id.isin(highschoolers)]

    """ Cleaning Credits Earned/Attempted"""
    for index, row in student_records.iterrows():
        if not row['grade'] or row['offering_id'] == 237136:
            # The grade is incomplete so no credits are taken or earned
            student_records.loc[index, ['credits_attempted', 'credits_earned']] = 0
            continue
        # Student completed the course and attempted 0.5 credits
        student_records.loc[index, 'credits_attempted'] = 0.5
        if row['grade'] not in ['Fail', 'F']:
            # Student passed and earned 0.5 credits
            student_records.loc[index, 'credits_earned'] = 0.5 
        else:
            # Student Failed and earned a 0
            student_records.loc[index, 'credits_earned'] = 0

    """ Getting Students GPAs """
    student_gpas = (
        student_records
        .assign(unweighted_numerator=lambda x: x['gpa_points'] * x['credits_earned'],
            weighted_numerator=lambda x: (x['gpa_points'] + x['weight']) * x['credits_earned']
            )
        .groupby('user_id')
        .sum()
        .assign(unweighted_gpa=lambda x: round(x['unweighted_numerator'] / x['credits_earned'], 2),
            weighted_gpa=lambda x: round(x['weighted_numerator'] / x['credits_earned'], 2)
            )
        [['unweighted_gpa', 'weighted_gpa']]
        .reset_index()
    )

    return {
        'gpas': student_gpas,
        'grades':student_records.drop(['first_name', 'last_name', 'level_description'], axis=1)
    }


def getPsatScores():
    """ Getting Students GPA Data """
    students = sky.getUsers()

    raw_psat_data = (readSpreadsheet(sheet_id="1bD5XuiLzjUpxQrdeOxWzjHyULD1uPKtHA_YHC0NPf0g")
                    .astype('int64')
                    )
    # Cleaning student data from api
    raw_student_data = students[['id', 'student_id']]
    raw_student_data = raw_student_data[~(raw_student_data.student_id == "")].astype('int64')

    # Merging with psat data
    psat_data = (
        raw_student_data
        .merge(raw_psat_data,
            'inner',
            on='student_id'
        )
        .rename(columns={
        'id':'user_id'
        })
        .drop('student_id', axis=1)
        .groupby('user_id')
        .max()
        .reset_index()
    )

    return psat_data

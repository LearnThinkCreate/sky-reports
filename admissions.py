import math
import pandas as pd
import numpy as np

from config import sky

def getCandidates():
    # Candidates from the Sky API
    candidates = sky.get('admissions/candidates')
    candidates.current_status = candidates.current_status.fillna('Needs Checklist') 

    # Checklist from Sky API 
    checklist = sky.get('admissions/checkliststatus')

    # Adding custom status_name 
    finished_application = checklist.loc[np.where(checklist.ordinal >= 3), 'status_name'].tolist()
    incomplete_application = checklist.loc[np.where(checklist.ordinal < 3), 'status_name'].tolist()
    candidates.loc[candidates.current_status.isin(finished_application), 'application_status'] = 'Finished Application'
    candidates.loc[~candidates.current_status.isin(incomplete_application), 'application_status'] = 'Finished Application'

    # Adding each candidates gender
    users = sky.getUsers('Candidate')[['id', 'gender', 'ethnicity']]
    candidates = candidates.merge(users, how='left', left_on='user_id', right_on='id')

    # Extracting the grade level from string
    candidates['grade_level'] = candidates.entering_grade.str.extract(r'(\d*)')

    # Pulling financial aid data from advanced list 
    financial_aid = sky.getAdvancedList(73845)['user_id'].astype('int64').tolist()
    candidates.loc[candidates.user_id.isin(financial_aid), 'financial_aid'] = True
    candidates.loc[~candidates.user_id.isin(financial_aid), 'financial_aid'] = False
    
    # Fields for db
    candidates = candidates[[
        'user_id', 'role', 'grade_level', 'gender', 'financial_aid',
        'entering_year', 'application_status', 'ethnicity'
    ]].rename(columns={
        'user_id':'id'
    })

    return candidates

def getContracts():
    # Pulling contracts from advanced list
    contracts = sky.getAdvancedList(73783)

    # Getting students for join
    students = sky.getAdvancedList(73113)[['user_id', 'grade_level']]
    students = students.drop_duplicates(ignore_index = True)

    # Joining data
    contracts = contracts.merge(students, on='user_id', how='left')
    contracts['grade'] = None

    # Cleaning grade level
    for index, row in contracts.iterrows():
        if row['role'] == "Student":
            if isinstance(row['grade_level'], float):
                if  math.isnan(row['grade_level']):
                    contracts.loc[index, 'grade'] = ''
                    continue
            contracts.loc[index, 'grade'] = (int(row['grade_level']) + 1)
        else:
            contracts.loc[index, 'grade'] = row['enter_grade']

    contracts = contracts[[
        'user_id', 'role', 'grade_level', 'gender',
        'not_returning', 'payment_plan', 'ethnicity', 'contract_year'
    ]]

    contracts = contracts.astype(object).where(pd.notnull(contracts), None)

    return contracts.drop_duplicates().reset_index(drop=True)
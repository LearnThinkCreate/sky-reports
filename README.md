# Python Sky Academic Reports

Python scripts to pull data from Blackbaud via the Sky API and upload into Google Sheets

# About

This repository is an example of how the [sky-api-python-client](https://github.com/LearnThinkCreate/sky-api-python-client) can be used in conjunction with Google Sheets to provide dynamic reporting for your school. 

The output are 2 Google Sheets
1. Sky Grades
    1. The grades of every student in the school for the current term
    2. This is used in a Tableau Dashboard in order to provide advisors a easy way to see all Students grades
2. Sky Attendance
    1. The number of absences for every student in each of their classes
    2. This is also used in a Tableau Dashboard so Admin and advisors can see students attendance at a glance


``` Python
from utils import *

# Updating gradebook grades spreadsheet
grades = getGradebookGrades()
updateSpreadsheet(grades, sheet_name = "Sky Grades")

# Updating absences spreadsheet
absences = getAbsences()
updateSpreadsheet(absences, sheet_name="Sky Attendance")

```

Note: Tampa Prep has used Gsuite for years so the integration with Google Sheets was done in order to maximize convenience and cost. However, another data solution could easily be integrated if that's what suits your school's needs.


# Under the Hood

## [Utilities](https://github.com/LearnThinkCreate/python-sky-reports/blob/main/utils.py)

While all the REST endpoints provided by Blackbaud are helpful, the one that I've utilized most has been the [Advanced List Endpoint](https://developer.sky.blackbaud.com/docs/services/school/operations/V1ListsAdvancedByList_idGet). 

Core Advanced Lists are important for a few reasons:
1. They provide access to data that is otherwise unavailable via the SKY API
2. They can provide runtime improvement to data that requires multiple calls to the Sky API

In the future I think it would be incredibly beneficial if developers could create Advanced List templates and share them out to the community. 

In the `utils.py` file there are 5 helper functions that all use the `sky.Sky.getAdvancedList` function in some way - `getAdvisors`. `getGradebookGrades`, `getEnrollments`, `getAttendance`, and `getAbsences`.

Some sample code:
``` Python
import numpy as np
import re

from sky import Sky
from dotenv import load_dotenv
from skydb.sheets import *

load_dotenv()
sky = Sky(file_path='credentials/sky_credentials.json')

def getAttendance():
    # Pulling attendance data
    attendance = sky.getAdvancedList(0000)

    # Being a good boy
    attendance = attendance.astype({
        "user_id":'int64',
        "absenceTypeId":'int64'
    })


    return attendance

def getEnrollments():
    # Pulling all grades from the current school year
    grades = sky.getAdvancedList(0000)

    academicEnrollment = grades[[
        'user_id',
        'firstname',
        'lastname', 
        'course_title', 
        'course_code', 
        'term_name',
        'block',
        'teacher_first',
        'teacher_last',
        'department_name',
        'advisor_id'
    ]].astype({
        "user_id":'int64'
    })

    return academicEnrollment
```

## [Google Sheets](https://github.com/LearnThinkCreate/sky-database/blob/main/src/skydb/sheets/google_sheets.py)

Inspired by [this guide](https://levelup.gitconnected.com/python-pandas-google-spreadsheet-476bd6a77f2b) on using pandas and gspread, this script provides 3 helper functions that make working with Google Sheets really easy -- `readSpreadsheet`, `updateSpreadsheet`, and `createSpreadsheet`. 

These functions are really just convenient wrappers around the [gspread library](https://docs.gspread.org/en/latest/oauth2.html). I highly recommend checking out these resources if you'd like to use Google Sheets and Python as a part of your schools reporting solution 

Some sample code:
``` Python
import pandas as pd
import gspread

def readSpreadsheet(
    sheet_name = None,
    sheet_id = None,
    tab_index = 0,
    ):

    gc = gspread.service_account()

    if sheet_name:
        gc = gc.open(sheet_name)
    else:
        gc = gc.open_by_key(sheet_id)

    values = gc.get_worksheet(tab_index).get_all_values()

    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)         
    
    return df

def createSpreadsheet(sheet_name, df):
    gc = gspread.service_account()

    sheet = gc.create(sheet_name)
    sheet.share("whyson@tampaprep.org", perm_type='user', role="writer")

    ## Inserting the df
    updateSpreadsheet(df, sheet_id=sheet.id)
    return sheet
```

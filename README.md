# Sky Academic Reports

## About

This repository uses the [sky-api-python-client](https://github.com/LearnThinkCreate/sky-api-python-client) and [skydb](https://github.com/LearnThinkCreate/sky-database) libraries to maintain Tampa Preparatory's school's data infrastructure.

## Goals 

1. Keep Google Cloud SQL database updated 
2. Update Google Sheets for use in Tableau Dashboards 
3. Update Blackbaud Data directly using the Sky API


## Configuration

- [cloud sql](https://github.com/LearnThinkCreate/sky-reports/blob/main/docs/cloud_sql.md)
- [google secret manager](https://github.com/LearnThinkCreate/sky-reports/blob/main/docs/google_secrets_manager.md)
- [app_engine](https://github.com/LearnThinkCreate/sky-reports/blob/main/docs/app_engine.md)

## Advanced List

While all the REST endpoints provided by Blackbaud are helpful, the one that I've utilized most has been the [Advanced List Endpoint](https://developer.sky.blackbaud.com/docs/services/school/operations/V1ListsAdvancedByList_idGet). 

Core Advanced Lists are important for a few reasons:
1. They provide access to data that is otherwise unavailable via the SKY API
2. They can provide runtime improvement to data that requires multiple calls to the Sky API

In the future I think it would be incredibly beneficial if developers could create Advanced List templates and share them out to the community. 

The most helpful use case for advanced list, in my experience, has been to pull current and historic grades. Both [grades.py](https://github.com/LearnThinkCreate/sky-reports/blob/main/grades.py) & [records.py](https://github.com/LearnThinkCreate/sky-reports/blob/main/records.py) are examples of this

Sample from grades.py:
``` Python
import os
import pandas as pd

from config import sky

def getRawGrades(current=True):
    """ Returns pd.DataFrame with student's current grades from the teacher's gradebooks  """
    # Reading advanced list SID from a environment variable
    raw_grades = sky.getAdvancedList(os.environ.get('SID_RG'))
    if not current:
        # Returning grades for the whole year
        return raw_grades
    # Filtering for the current acadmeic turn
    grades = raw_grades[raw_grades.term.isin(sky.getTerm(active=True))].reset_index(drop=True)
    grades.last_updated = pd.to_datetime(grades.last_updated)
    return grades
```

## Main.py

In order to keep the cloud sql database updated I've decided to create a flask app that runs on Google App Engine and is updated by Google Cloud Scheduler.

**Importing functions**
``` Python
# All helper functions
from utils import *
# Classes and tables defined in skdb
from skydb.classes import *
from skydb.sheets import updateSpreadsheet
from skydb.update import updateTable
```

**Loading Token from cloud storage**
``` Python
from google.cloud import storage

app = Flask(__name__)

# Loading the api token
storage_client = storage.Client()
bucket = storage_client.bucket('sky-api-326214.appspot.com')
BLOB = bucket.blob('.sky-token')
# Storing token in a tmp folder where it will be updated after each api call
BLOB.download_to_filename('/tmp/.sky-token')
```

**Defining routes to update data**
``` Python
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
    return "Hello Users"')
```

**Updating Google Sheets for use in Tableau**
``` Python
@app.route('/legacy')
def updateSpreadSheets():
    grades = legacyGradeReport()
    absences = getAbsences().reset_index()
    updateSpreadsheet(grades.astype(str), sheet_name = "Sky Grades")
    updateSpreadsheet(absences.astype(str), sheet_name="Sky Attendance")
    # Saving the token to Google Cloud Storage
    BLOB.upload_from_filename('/tmp/.sky-token')
    return "Hello new spreadsheet data"
```
[**check out cron.yaml to see how cloud scheduler updates the data**](https://github.com/LearnThinkCreate/sky-reports/blob/main/cron.yaml)

## Ad-Hoc Reporting

**Providing science teachers the data they need to make student course recommendations**
``` Python
import gspread
from utils import *
from skydb.sheets import updateSpreadsheet, createSpreadsheet

# Getting official records
records = getOfficialRecords()
grades = records['grades']
gpas = records['gpas']
students = getStudents().drop(['birth_date'], axis=1)
psat_scores = getPsatScores()

""" PSAT Scores """
psat_students = (
    students
    .query("""grade_level in [9,10,11]""")
    .drop('counselor', axis=1)
    .rename(columns={'id':'user_id'})
    .astype({'user_id':'int64', 'student_id':'float', 'grade_level':'int64'})
    .merge(psat_scores,
                'left',
                on='user_id'
    )
)

""" Cumulative GPA """
gpa_students = (
    psat_students
    .merge(gpas,
           'inner',
           on='user_id'
    )
)

### Some data cleaning ...

""" Joining with student Data """
science_data = (
    gpa_students
    .merge(clean_science_students,
           'inner',
           on='user_id'
    )
    .sort_values(['last_name', 'first_name'])
    .drop(['user_id', 'student_id', 'first_name'], axis=1)
)

updateSpreadsheet(science_data.fillna(''), 
                   sheet_id='1yf0CHCaG39S7gL65YOOVrPNgIqVyluC4fT1frQkSGRo',
                   styleClass=HysonFireStyle
                  )
```

import os
import pandas as pd

from config import sky
from users import getAdvisors
from academics import getEnrollments

def getAttendance():
    """ Legacy Function for use in Tableau """
    # Pulling attendance data
    attendance = sky.getAdvancedList(os.environ.get('SID_AT'))
    attendance = attendance.astype({"absenceTypeId":'int64'})
    attendance.absence_date = pd.to_datetime(attendance.absence_date)
    return attendance


def getAbsences():
    """ Legacy function that is used for Tableau """
    raw_attendance = getAttendance()
    
    # Filtering for absences
    attendance = raw_attendance.loc[raw_attendance.absenceTypeId == 6702, ].reset_index(drop=True)
    attendance = attendance.groupby(
        ['user_id', 'course_title', 'block', 'absence_date']
        ).count()['enrolled'
        ].rename('absences'
        ).reset_index(
        ).sort_values(['user_id', 'block']
        ).drop_duplicates()

    
    # Pulling students full enrollment
    academicEnrollment = getEnrollments()
    
    # Joining with the attendance data
    absenceList = academicEnrollment.merge(attendance,'left') .merge(getAdvisors(),'inner')

    # Adding a Full Name Column
    absenceList['full_name'] = absenceList['lastname'] + ", " + absenceList['firstname']

    # Cleaning na values
    absenceList['absences'] = absenceList['absences'].fillna(0)
    absenceList = absenceList.fillna("")

    # Cleaning records 
    absenceList = absenceList.merge(
            absenceList.groupby(
            ['user_id', 'course_title']
            ).nunique()['teacher_last'
            ].rename( 'num_teachers'
            ).reset_index()
        ).sort_values(
            ['advisor_last', 'lastname', 'block', 'course_title']
            )
    
    # Removing duplicates from the absence calculation
    absenceList = absenceList.assign(absences = absenceList.absences / absenceList.num_teachers)

    absenceList.reset_index(inplace = True)

    return absenceList

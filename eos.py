
from grades import getSemesterGrades
from google_sheets import HysonFireStyle, hideBody, applyAlternatingColors, clearAlternatingColors

from skydb.sheets import createSpreadsheet, updateSpreadsheet
from skydb.sheets.google_sheets import _get_gc


def filterGradeData(grade_data, level_description='UpperSchool'):
    data = grade_data.loc[grade_data.level_description == level_description]
    data = data.drop('level_description', axis=1)
    return data

def createEosReport(report_type='S1', level_description="All"):
        if level_description == 'All':
            ms = True
            us = True
        elif level_description == 'US':
            us = True
        elif level_description == "MS":
            ms = True
        else:
            raise ValueError('Invalid level description')
          
        grade_data = getSemesterGrades(report_type, report=True)
        
        if us:
            data = filterGradeData(grade_data, 'Upper School')
            sheet = createSpreadsheet(data.astype('str').fillna(''), 
                                      f'Upper School {report_type} Grade Report', 
                                      styleClass=HysonFireStyle
                                     )
            
            # Hiding the user_id field
            sheet.batch_update(hideBody(start=len(data.columns) - 1))
            worksheet = sheet.sheet1
            applyAlternatingColors(data, worksheet)
            
            print(f"US Sheet ID is {sheet.id}")
        if ms:
            data = filterGradeData(grade_data, 'Middle School')
            sheet = createSpreadsheet(data.astype('str').fillna(''), 
                                      f'Middle School {report_type} Grade Report', 
                                      styleClass=HysonFireStyle
                                     )
            # Hiding the user_id field
            sheet.batch_update(hideBody(start=len(data.columns) - 1))
            worksheet = sheet.sheet1
            applyAlternatingColors(data, worksheet)
            print(f"MS Sheet ID is {sheet.id}")

def updateEosReport(level_description="All"):
    if level_description == 'All':
        ms = True
        us = True
    elif level_description == 'US':
        us = True
    elif level_description == "MS":
        ms = True
    else:
        raise ValueError('Invalid level description')
    
    # Gettting the grade data 
    grade_data = getSemesterGrades("MS2", report=True)
    
    gc = _get_gc()
    
    if us:
        sheet_id = '1VBNH2BCBZzDoM7eGKNQdZX-R4MoD3c_6JFIRUs3J6mQ'
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        
        data = filterGradeData(grade_data, 'Upper School')
        # Clearning the format
        clearAlternatingColors(worksheet)
        # Updating cell values
        updateSpreadsheet(data, sheet_id=sheet_id)
        # Reapplying alternate colors
        applyAlternatingColors(data, worksheet)
    if ms:
        sheet_id = '1vGHBC3PvyCfxOpkMKX4-ytb_4m7tEQishAILBSt2xGM'
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        
        data = filterGradeData(grade_data, 'Middle School')
        # Clearning the format
        clearAlternatingColors(worksheet)
        # Updating cell values
        updateSpreadsheet(data, sheet_id=sheet_id)
        # Reapplying alternate colors
        applyAlternatingColors(data, worksheet)
    
    
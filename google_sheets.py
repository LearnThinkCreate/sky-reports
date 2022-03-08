from skydb.sheets.style import BaseStyle
import matplotlib.colors as mcolors
from gspread_formatting import *
from string import ascii_uppercase

class HysonFireStyle(BaseStyle):
    def style(self, ncol=100):
        set_frozen(self.worksheet, rows=1, cols=2)
        """ Body """
        self.worksheet.format(':', {
                'horizontalAlignment': 'CENTER',
                'textFormat':{
                    'fontSize': 12
                },
            # 'wrapStrategy': 'WRAP',
            })

        """ Header """
        # Bold
        self.worksheet.format('1:', {'textFormat': {'bold': True, 'fontSize':12}})
        # Background color
        self.worksheet.format('1:', self.mplColorConverter(color='lightgrey'))

        self.worksheet.columns_auto_resize(0, ncol)


class HysonWaterStyle(BaseStyle):
    """ """
    def style(self, ncol=100):
        set_frozen(self.worksheet, rows=1, cols=2)
        fmt = cellFormat(backgroundColor=self.mplColorConverter('lightcoral'),
                        # textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
                         horizontalAlignment='CENTER'
                        )
        
        fmt2 = cellFormat(backgroundColor=self.mplColorConverter('navajowhite'),
                          horizontalAlignment='RIGHT'
                         )

        format_cell_ranges(self.worksheet, [('A:D10', fmt), ('A15:D30', fmt2)])


    def mplColorConverter(self, col):
        col = mcolors.to_rgb(col)
        return color(col[0], col[1], col[2])
        

def mplColorConverter(col):
    col = mcolors.to_rgb(col)
    return color(col[0], col[1], col[2])


def getLetters():
    return list(ascii_uppercase)


def hideBody(start=5, end=7):
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "properties": {
                        "hiddenByUser": True
                    },
                    "range": {
                        "dimension": "COLUMNS",
                        "startIndex": start,
                        "endIndex": end
                    },
                    "fields": "hiddenByUser"
                }
            }
        ]
    }
    return body


def applyAlternatingColors(df, worksheet, group='user_id', col='navajowhite'):
    df_index = (
        df
        .reset_index(drop=True)
        .reset_index()
        .groupby(group, sort=False)['index']
        .agg([('start','first'),('end','last')])
        .reset_index()
    )
    
    letters = getLetters()
    first_letter = 'A'
    last_letter = letters[(len(df.columns) - 1)]

    format_list = []

    fmt = cellFormat(backgroundColor=mplColorConverter(col),
                    # textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
                    # horizontalAlignment='CENTER'
                    )
    
    # Looping over every other student
    odd_index = list(range(1, len(df_index), 2))
    for index, row in df_index.iloc[odd_index].iterrows():
        format_list.append((
            # Adding 2 since sheets indexes at 1 and has header
            (first_letter + str(row['start'] + 2 ) + ':' + last_letter + str(row['end'] + 2)),
            fmt
        ))
    format_cell_ranges(worksheet, format_list)


def clearAlternatingColors(worksheet):
    # Clearning the format
    worksheet.format(f"A2:{getLetters()[len(worksheet.get_all_values()[0]) - 1]}{len(worksheet.get_all_values())}", {
        "backgroundColor": {
          "red": 1,
          "green": 1,
          "blue": 1
        }
    })
    return True

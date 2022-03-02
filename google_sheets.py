from skydb.sheets.style import BaseStyle
from gspread_formatting import *

class HysonFireStyle(BaseStyle):
    def style(self, ncol=100):
        set_frozen(self.worksheet, rows=1, cols=2)
        """ Body """
        self.worksheet.format(':', {
                'horizontalAlignment': 'CENTER',
                'textFormat':{
                    'fontSize': 14
                },
            #  'wrapStrategy': 'WRAP',
            })

        """ Header """
        # Bold
        self.worksheet.format('1:', {'textFormat': {'bold': True, 'fontSize':12}})
        # Background color
        self.worksheet.format('1:', self.mplColorConverter(color='lightgrey'))

        self.worksheet.columns_auto_resize(0, ncol)
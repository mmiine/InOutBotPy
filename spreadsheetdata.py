import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import warnings

def Authorize(sheetnum=1):
    #Authorize the API
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)

    #Fetch the sheet
    if(sheetnum==2):
        sheet = client.open('Study-Tracker-Sheet').get_worksheet(1)
    else:
        sheet = client.open('Study-Tracker-Sheet').get_worksheet(0)
    return sheet



def Update_Sheet(name, time, sheet=None):
    # Update Cell
    if(sheet==None):
        sheet=Authorize()
    try:
        nLocation=sheet.find(name)
    except:
        sheet.update_cell(1,sheet.row_values(1).__len__()+1, name)
    try:
        today = date.today()
        today =str(today)
        tLocation = sheet.find(today)
    except:
        today = str(date.today())
        sheet.append_row([today], table_range='A1')

    nLocation = sheet.find(name)
    tLocation = sheet.find(today)

    cell = sheet.cell(tLocation.row,nLocation.col)
    if cell.value==None:
        cell.value='0'
    writeTime=time
    writeTime=  "{:.2f}".format(writeTime)
    writeTime = str(writeTime.replace('.',','))
    sheet.update_cell(tLocation.row,nLocation.col, writeTime)



def Initial_Read_Data(name, sheet=None):
    if (sheet == None):
        sheet = Authorize()
    try:
        nLocation = sheet.find(name)
    except:
        warnings.warn("User name couldn't found in sheet")
        with warnings.catch_warnings(record=True) as w:
            return -1
    try:
        today = date.today()
        today = str(today)
        tLocation = sheet.find(today)
    except:
        warnings.warn("Date couldn't found in sheet")
        with warnings.catch_warnings(record=True) as w:
            return -1
    nLocation = sheet.find(name)
    tLocation = sheet.find(today)

    cell = sheet.cell(tLocation.row, nLocation.col)
    value = cell.value
    value = float(value.replace(',','.'))

    sheet2 = Authorize(2)
    try:
        nLocation = sheet.find(name)
    except:
        warnings.warn("User name couldn't found in sheet")
        with warnings.catch_warnings(record=True) as w:
            return -1
    nLocation = sheet2.find(name)
    cell = sheet2.cell(nLocation.row, 2)
    Svalue = cell.value
    Svalue = float(Svalue.replace(',', '.'))
    return value,Svalue



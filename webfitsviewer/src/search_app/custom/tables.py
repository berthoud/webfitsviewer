# tables.py

from flask_table import Table, Col, LinkCol

class CountTotal(Table):
    total = Col('Total')

class ResultsFile(Table):
    file_path = Col('File Path', show=True)
    simple = Col('Simple', show=True)
    date_obs = Col('Date_obs')
    bitpix = Col('Bitpix')
    ra = Col('Ra')
    dec_ = Col('dec_')
    exptime = Col('exptime')
    #edit = LinkCol('Edit', 'edit_file_view', url_kwargs=dict(id='file_path'))

class Results_Cq1(Table):
    groupId = Col('Group Id', show=True)
    startDate = Col('Start Observation')
    endDate = Col('End Observation')
    fileId = Col('File Id', show=True)
    date = Col('Date')

class Results_Cq2(Table):
    groupId = Col('Group Id', show=True)
    fileId = Col('File Id', show=True)
    objectName = Col('Object Name')
    dayId = Col('Date', show=True)
    moonPhase = Col('Moon Phase')

class Results_Cq3(Table):
    groupId = Col('Group Id', show=True)
    startDate = Col('Start Date')
    startTime = Col('Start Time')
    endDate = Col('End Date')
    endTime = Col('End Time')
    description = Col('Description')

class Results_Cq4(Table):
    fileId = Col('File Id', show=True)
    groupId = Col('Group Id', show=True)
    objectName = Col('Object Name')
    date = Col('Date')
    time = Col('Time')
    timeStamp = Col('Time Stamp')
    reductionStage = Col('Reduction Stage')
    fileType = Col('File Type')
    quality = Col('Quality')
    position = Col('Position')
    bandType = Col('Band Type')

class Results_Cq5(Table):
    objectName = Col('Object Name')
    filesTotal = Col('Total_Files')
    bandsTotal = Col('Total_Band_Types')
    totalDays = Col('Total_Days')

class Results_Sq2(Table):
    groupId = Col('Group Id', show=True)
    startDate = Col('Start Date (ASCENDING)')
    startTime = Col('Start Time')
    endDate = Col('End Date')
    endTime = Col('End Time')
    description = Col('Description')

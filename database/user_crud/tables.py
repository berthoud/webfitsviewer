from flask_table import Table, Col, LinkCol

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


class SearchMoon(Table):
    dayId = Col('Date', show=True)
    moonPhase = Col('Moon Phase')
    
class CountTotal(Table):
    total = Col('Total')

class Results(Table):
    userId = Col('User Id', show=True)
    firstName = Col('First Name')
    lastName = Col('Last Name')
    email = Col('Email')
    password = Col('Password', show=False)
    permissions = Col('Permissions')
    edit = LinkCol('Edit', 'edit_view', url_kwargs=dict(id='userId'))
    delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='userId'))

class ResultsFile(Table):
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
    edit = LinkCol('Edit', 'edit_file_view', url_kwargs=dict(id='fileId'))
    delete = LinkCol('Delete', 'delete_file', url_kwargs=dict(id='fileId'))
    
class ResultsObs(Table):
    groupId = Col('Group Id', show=True)
    startDate = Col('Start Date')
    startTime = Col('Start Time')
    endDate = Col('End Date')
    endTime = Col('End Time')
    description = Col('Description')
    edit = LinkCol('Edit', 'edit_obs_view', url_kwargs=dict(id='groupId'))
    delete = LinkCol('Delete', 'delete_obs', url_kwargs=dict(id='groupId'))

class ResultsWD(Table):
    dayId = Col('Date', show=True)
    sunriseTime = Col('Sunrise Time')
    sundownTime = Col('Sundown Time')
    moonPhase = Col('Moon Phase')
    edit = LinkCol('Edit', 'edit_wd_view', url_kwargs=dict(id='dayId'))
    delete = LinkCol('Delete', 'delete_wd', url_kwargs=dict(id='dayId'))



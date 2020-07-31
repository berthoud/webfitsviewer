from flask_table import Table, Col, LinkCol
 
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

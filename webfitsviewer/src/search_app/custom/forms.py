# forms.py

from wtforms import Form, StringField, SelectField, TextAreaField, TextField, validators
from wtforms.validators import DataRequired, Email

class Moon_SearchForm(Form):
    select = StringField('Search Weather Days by Moon Phase:', validators=[DataRequired()])
    search = StringField('')
    
class S_SearchForm(Form):
    print("S_searchForm")
    choices = [('Files', 'Files'),
               ('Observations', 'Observations'),
               ('Users', 'Users'),
               ('Day Weather', 'Day Weather')]
               
    name = TextField('File path:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
    
    select_file = SelectField('Search for :', choices=choices)
    search_file = StringField('')
    search_date = StringField('')
    search_ra = StringField('')
    search_dec = StringField('')
    search_exptime = StringField('')
    


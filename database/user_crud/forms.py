# forms.py

from wtforms import Form, StringField, SelectField, TextAreaField
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
    select = SelectField('Search for :', choices=choices)
    search = StringField('')
    


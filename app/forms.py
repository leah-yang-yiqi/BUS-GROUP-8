from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields import FileField
from flask_wtf.file import FileRequired, FileAllowed

class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class SelectForm(FlaskForm):
    day=SelectField("day",choices = [(1, 'Monday'), (2, 'Tuesday'), (3,'Wednesday'),
                                     (4,'Thursday'),(5,'Friday')])
    hour=IntegerField("hour",validators=[DataRequired(),NumberRange(9,17)])
    item=StringField("item",validators=[DataRequired()])
    submit_f = SubmitField('Submit')

class CSVUploadForm(FlaskForm):
        file = FileField('Upload', validators=[FileRequired(), FileAllowed(['csv'])])
        submit = SubmitField('Submit')
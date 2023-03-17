from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    tl_id = StringField('Team leader id', validators=[DataRequired()])
    work_size = StringField('Объем работы', validators=[DataRequired()])
    collaborators = TextAreaField("Работники")
    is_finished = BooleanField("Работа выполнена?")
    submit = SubmitField('Применить')

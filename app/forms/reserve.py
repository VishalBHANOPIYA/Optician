from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Optional, Length

class ReserveForm(FlaskForm):
    message = TextAreaField("Message (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Reserve at Store")

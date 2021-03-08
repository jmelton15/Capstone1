from flask_wtf import FlaskForm
from wtforms import StringField,FloatField,SelectField,PasswordField,TextAreaField
from wtforms.validators import InputRequired,Optional,Email,ValidationError,Length
from models import db, connect_db,User


class RouteForm(FlaskForm):
    """ Form for a user to input all their travel route information
    """
    start_point = StringField("Starting Location", validators=[InputRequired()])
    end_point = StringField("Destination", validators=[InputRequired()])
    way_points = TextAreaField("Stops Along The Way (i.e. Park, museum, food genre, spa, etc.)",
                           validators=[InputRequired()])
    
class SignUpForm(FlaskForm):
    """Form for a user to sign-up and create an account
    """
    username = StringField("Create A Username", validators=[InputRequired(),Length(max=20)])
    email = StringField("Enter Email", validators=[InputRequired(),Email()])
    password = PasswordField("Create A Password", validators=[InputRequired()])
    confirm_pass = PasswordField("Confirm Password", validators=[InputRequired()])
    
    
    def validate_confirm_pass(self,field):
        """ Custom validation function that makes sure the two passwords
            entered are the same
        """
        if field.data != self.password.data:
            raise ValidationError("Passwords Don't Match")
        
class LoginForm(FlaskForm):
    """Form for a user to login
    """
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class EditUsername(FlaskForm):
    """ Form for editing username in profile
    """
    username = StringField("New Username",validators=[InputRequired()])
    

    
class EmailConfirmationForm(FlaskForm):
    """Form for sending email to users email if they forgot password
    """
    email = StringField("Enter Email", validators=[InputRequired(),Email()])
    confirm_email = StringField("Confirm Email", validators=[InputRequired(),Email()])
    
    def validate_confirm_email(self,field):
        """ Custom validation function that makes sure the two emails
            entered are the same
        """
        if field.data.lower() != self.email.data.lower():
            raise ValidationError("Emails Don't Match")

class PasswordResetForm(FlaskForm):
    """ Form for resetting user's password
    """
    password = PasswordField("Create A New Password", validators=[InputRequired()])
    confirm_pass = PasswordField("Confirm New Password", validators=[InputRequired()])
    
    def validate_confirm_pass(self,field):
        """ Custom validation function that makes sure the two passwords
            entered are the same
        """
        if field.data != self.password.data:
            raise ValidationError("Passwords Don't Match")
    
    

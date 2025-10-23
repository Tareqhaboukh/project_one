from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeField, DateField, DecimalField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, InputRequired, ValidationError, Optional
from models import Vendors

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create New User')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Edit User')

class LogInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

class ChangePassword(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Change Password")

class CheckPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Check Password")

class ResetPassword(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField("Reset Password")

class VendorForm(FlaskForm):
    vendor_name = StringField('Vendor Name', validators=[DataRequired(), Length(max=120)])
    business_type = StringField('Business Type', validators=[Optional(), Length(max=100)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Submit Vendor')

class EditVendorForm(FlaskForm):
    vendor_name = StringField('Vendor Name', validators=[DataRequired(), Length(max=120)])
    business_type = StringField('Business Type', validators=[Optional(), Length(max=100)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Edit Vendor')

class InvoiceForm(FlaskForm):
    pdf_file = FileField('Upload PDF (optional)', validators=[Optional()])
    
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    vendor_id = SelectField('Vendor', coerce=int, validators=[InputRequired()])
    amount = DecimalField('Amount', validators=[NumberRange(min=0), DataRequired()])
    tax = DecimalField('Tax', validators=[NumberRange(min=0), Optional()])
    description = StringField('Description', validators=[Optional()])
    
    submit = SubmitField('Submit Invoice')

    def set_vendor_choices(self):
        choices = [(0, "-- Select Vendor --")]
        choices += [(v.id, v.vendor_name) for v in Vendors.query.all()]
        self.vendor_id.choices = choices

    def validate_vendor_id(self, field):
        if field.data == 0:
            raise ValidationError("Please select a vendor")
        
class EditInvoiceForm(FlaskForm):
    pdf_file = FileField('Upload PDF (optional)', validators=[Optional()])
    
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    vendor_id = SelectField('Vendor', coerce=int, validators=[InputRequired()])
    amount = DecimalField('Amount', validators=[NumberRange(min=0), DataRequired()])
    tax = DecimalField('Tax', validators=[NumberRange(min=0), Optional()])
    description = StringField('Description', validators=[Optional()])
    
    submit = SubmitField('Submit Invoice')

    def set_vendor_choices(self):
        choices = [(0, "-- Select Vendor --")]
        choices += [(v.id, v.vendor_name) for v in Vendors.query.all()]
        self.vendor_id.choices = choices

    def validate_vendor_id(self, field):
        if field.data == 0:
            raise ValidationError("Please select a vendor")
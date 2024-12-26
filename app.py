from flask import Flask, request, redirect, render_template, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Users {self.username}>'
    
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_passwords(self, password):
        return check_password_hash(self.password_hash, password)

class UserForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    old_password = PasswordField('Old Password')
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET'])

def users():
    users = Users.query.all()
    return render_template('users.html',
                           users=users)

@app.route('/user/profile/<int:id>', methods=['GET','POST'])

def user_profile(id):
    form=UserForm()
    user_profile = Users.query.get_or_404(id)

    if request.method == 'POST':
        password_entered = form.password.data

        if check_password_hash(user_profile.password_hash, password_entered):
            flash('Password is correct!')
        else:
            flash('Incorrect password.')

    return render_template('user_profile.html',
                           form=form,
                           user_profile=user_profile)


@app.route('/user/add', methods=['GET','POST'])

def user_add():
    form = UserForm()

    if form.validate_on_submit():
        existing_user = Users.query.filter_by(username=form.username.data).first()
        
        if existing_user:
            flash('User already exists!')
            return render_template('user_add.html', form=form)
        
        new_user = Users(username=form.username.data,
                         first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         email=form.email.data
            )
        
        new_user.hash_password(form.password.data)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully')
            return redirect(url_for('user_add'))

        except Exception as e:
            db.session.rollback()
            flash('Something went wrong')

    return render_template('user_add.html',
                           form=form)

@app.route('/user/edit/<int:id>', methods=['GET','POST'])

def user_edit(id):
    form = UserForm()
    user_to_edit = Users.query.get_or_404(id)

    if form.validate_on_submit():
        old_password = form.old_password.data

        if not check_password_hash(user_to_edit.password_hash, old_password):
            flash('password entered does not match the old password.')
            return render_template('user_edit.html', form=form, user_to_edit=user_to_edit)
        
        user_to_edit.username = form.username.data
        user_to_edit.first_name = form.first_name.data
        user_to_edit.last_name = form.last_name.data
        user_to_edit.email = form.email.data

        if form.password.data:
            user_to_edit.hash_password(form.password.data)

        try:
            db.session.add(user_to_edit)
            db.session.commit()
            flash('User edited successfully.')
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong while updating user.')
        return redirect(url_for('user_profile', id=user_to_edit.id))
    
    return render_template('user_edit.html',
                        user_to_edit=user_to_edit,
                        form=form)

@app.route('/user/delete/<int:id>')

def user_delete(id):
    user_to_delete = Users.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User has been deleted.')

    except Exception as e:
        db.session.rollback()
        flash('Something went worng.')
    
    return redirect(url_for('users'))


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
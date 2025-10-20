from flask import Flask, request, session, redirect, render_template, url_for, flash
from models import db, Users, Vendors
from flask_migrate import Migrate
from forms import *
from api import api_blueprints
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, current_user , login_user, login_required, logout_user
from flask_cors import CORS
import os

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    CORS(app)

    with app.app_context():
        db.create_all()
        from data_seed import seed_all
        seed_all()
    return app

app = create_app()

for blueprint in api_blueprints:
    app.register_blueprint(blueprint)

@login_manager.user_loader
def user_load(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=["GET","POST"])
def login():
    form = LogInForm()
    users = Users.query.all()
        
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(username=form.username.data).first()
        password_entered = form.password.data
        
        if existing_user:
            if existing_user.check_password(password_entered):
                login_user(existing_user)
                return redirect(url_for('user_profile'))
            else:
                flash('Incorrect password.')
        else:
            flash('incorrect username or password')

    return render_template('login.html',
                           form=form,
                           users=users)

@app.route('/guest_login')
def guest_login():
    guest_user = Users.query.filter_by(username='guest').first()
    if guest_user:
        login_user(guest_user)
        session['is_guest'] = True
        flash('You are logged in as Guest.', 'info')
        return redirect(url_for('user_profile'))
    else:
        flash('Guest user does not exist.')
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET','POST'])
@login_required

def logout():
    logout_user()
    session.clear()
    flash('user logged out successfully')
    return redirect(url_for('login'))


@app.route('/user', methods=['GET'])
def users():
    users = Users.query.all()
    return render_template('user.html',
                           users=users)

@app.route('/user/profile', methods=['GET','POST'])
@login_required

def user_profile():
    form = CheckPassword()

    if form.validate_on_submit():
        password_entered = form.password.data

        if current_user.check_password(password_entered):
            flash('Password is correct!')
        else:
            flash('Incorrect password.')
    return render_template('user_profile.html',
                           form=form if not session.get('is_guest') else form,
                           guest=session.get('is_guest', False),
                           users=Users.query.all()
    )

@app.route('/user/change_password', methods=['GET','POST'])
@login_required

def change_password():

    if session.get('is_guest'):
        flash("Guests cannot change password.")
        return redirect(url_for('user_profile'))
    
    form = ChangePassword()

    if form.validate_on_submit():
        old_password = form.old_password.data

        if current_user.check_password(old_password):
            if form.password.data:
                current_user.hash_password(form.password.data)

                try:
                    db.session.add(current_user)
                    db.session.commit()
                    flash('password changed successfully.')

                except Exception as e:
                    db.session.rollback()
                    flash('Something went wrong.')
                return redirect(url_for('user_profile'))

        else:    
            flash('password entered does not match the old password.')
    
    return render_template('change_password.html',
                        form=form)

@app.route('/reset_password',methods=['GET','POST'])
def reset_password():
    form = ResetPassword()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            user.hash_password(form.password.data)
            try:
                db.session.commit()
                flash('Password reset successful!')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Something went wrong, please try again.')
        else:
            flash('User does not exist.')
    return render_template('reset_password.html',
                           form=form)


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
            login_user(new_user)
            flash('User added successfully')
            return redirect(url_for('user_profile'))

        except Exception as e:
            db.session.rollback()
            flash('Something went wrong')

    return render_template('user_add.html',
                           form=form)

@app.route('/user/edit', methods=['GET','POST'])
@login_required

def user_edit():

    if session.get('is_guest'):
        flash("Guests cannot edit user.")
        return redirect(url_for('user_profile'))
    form = UserEditForm()

    if form.validate_on_submit():
        
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data

        try:
            db.session.add(current_user)
            db.session.commit()
            flash('user edited successfully.')
        except Exception as e:
            db.session.rollback()
            flash('something went wrong while updating user.')
        #return redirect(url_for('user_profile'))
    
    return render_template('user_edit.html',
                           form=form)

@app.route('/user/delete', methods=['GET','POST'])
@login_required

def user_delete():

    if session.get('is_guest'):
        flash("Guests cannot delete profile.")
        return redirect(url_for('user_profile'))

    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash('user has been deleted successfully.')

    except Exception as e:
        db.session.rollback()
        flash('something went worng.')
    
    return redirect(url_for('login'))

@app.route('/ping')
def ping():
    return 'OK', 200

@app.route('/user/invoice')
@login_required

def invoice():
    return render_template('invoice.html')

@app.route('/analytic')
@login_required

def analytic():
    return render_template('analytic.html')

########## Vendors ##########

@app.route('/vendor/add', methods=['GET', 'POST'])
@login_required

def vendor_add():
    form = VendorForm()

    if form.validate_on_submit():
        new_vendor = Vendors(
            vendor_name=form.vendor_name.data,
            business_type=form.business_type.data,
            tax_id=form.tax_id.data,
            country=form.country.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            created_by=current_user.username
        )
        db.session.add(new_vendor)
        db.session.commit()
        flash('Vendor added successfully!')
        return redirect(url_for('user_profile'))

    return render_template('vendor_add.html', form=form)

@app.route('/vendor/edit/<int:vendor_id>', methods=['GET', 'POST'])
@login_required
def vendor_edit(vendor_id):
    from models import Vendors
    from app import db

    vendor = Vendors.query.get_or_404(vendor_id)

    form = VendorForm(obj=vendor)

    if form.validate_on_submit():
        vendor.vendor_name = form.vendor_name.data
        vendor.business_type = form.business_type.data
        vendor.tax_id = form.tax_id.data
        vendor.country = form.country.data
        vendor.city = form.city.data
        vendor.postal_code = form.postal_code.data
        db.session.commit()
        flash('Vendor updated successfully!')
        #return redirect(url_for('vendor'))

    return render_template('vendor_edit.html', form=form, vendor=vendor)

@app.route('/vendor/view/<int:vendor_id>')
@login_required
def vendor_view(vendor_id):
    vendor_obj = Vendors.query.get_or_404(vendor_id)
    return render_template("vendor_view.html", vendor=vendor_obj)

@app.route('/vendor', methods=['GET', 'POST'])
@login_required
def vendor():
    search_query = ""
    vendors_list = []

    if request.method == "POST":
        search_query = request.form.get("search", "").strip()
        if search_query:
            vendors_list = Vendors.query.filter(Vendors.vendor_name.ilike(f"%{search_query}%")).all()
        else:
            vendors_list = Vendors.query.all()
    else:
        vendors_list = Vendors.query.all()

    return render_template("vendor.html", vendors=vendors_list, search_query=search_query)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
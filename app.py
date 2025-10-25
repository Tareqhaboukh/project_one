from flask import Flask, request, session, redirect, render_template, url_for, flash, jsonify
from models import db, Users, Vendors, Invoices, table_to_json
from flask_migrate import Migrate
from forms import *
from api import api_blueprints
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, current_user , login_user, login_required, logout_user
from flask_cors import CORS
from datetime import datetime, timezone
from utilities import parse_invoice_pdf
from google import genai
from sqlalchemy import func
import json
import sqlite3
import re
import os

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True

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

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LogInForm()
    users = Users.query.all()
        
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(username=form.username.data).first()
        password_entered = form.password.data
        
        if existing_user:
            if existing_user.check_password(password_entered):
                login_user(existing_user)
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password.')
        else:
            flash('Incorrect username or password')

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
        return redirect(url_for('dashboard'))
    else:
        flash('Guest user does not exist.')
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET','POST'])
@login_required

def logout():
    logout_user()
    session.clear()
    flash('User logged out successfully')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET','POST'])
@login_required

def dashboard():
    form = CheckPassword()

    if form.validate_on_submit():
        password_entered = form.password.data

        if current_user.check_password(password_entered):
            flash('Password is correct!')
        else:
            flash('Incorrect password.')
    return render_template('dashboard.html',
                           form=form if not session.get('is_guest') else form,
                           guest=session.get('is_guest', False),
                           users=Users.query.all()
    )

########## Users ##########

@app.route('/user_profile')
@login_required

def user_profile():
    return render_template('user_profile.html', user=current_user)

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
            return redirect(url_for('dashboard'))

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
        return redirect(url_for('dashboard'))
    form = UserEditForm()

    if form.validate_on_submit():
        
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data

        try:
            db.session.add(current_user)
            db.session.commit()
            flash('User edited successfully.')
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong while updating user.')
        #return redirect(url_for('dashboard'))
    
    return render_template('user_edit.html',
                           form=form)

@app.route('/user/delete', methods=['GET','POST'])
@login_required

def user_delete():

    if session.get('is_guest'):
        flash("Guests cannot delete profile.")
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash('User has been deleted successfully.')

    except Exception as e:
        db.session.rollback()
        flash('Something went worng.')
    
    return redirect(url_for('login'))

@app.route('/user/change_password', methods=['GET','POST'])
@login_required

def change_password():

    if session.get('is_guest'):
        flash("Guests cannot change password.")
        return redirect(url_for('dashboard'))
    
    form = ChangePassword()

    if form.validate_on_submit():
        old_password = form.old_password.data

        if current_user.check_password(old_password):
            if form.password.data:
                current_user.hash_password(form.password.data)

                try:
                    db.session.add(current_user)
                    db.session.commit()
                    flash('Password changed successfully.')

                except Exception as e:
                    db.session.rollback()
                    flash('Something went wrong.')
                return redirect(url_for('dashboard'))

        else:    
            flash('Password entered does not match the old password.')
    
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

@app.route('/users', methods=['GET'])
def users():
    users = Users.query.all()
    return render_template('user_list.html',
                           users=users)

########## Invoices ##########

@app.route('/invoice', methods=['GET', 'POST'])
@login_required

def invoice_list():
    invoices_list = Invoices.query.join(Vendors).order_by(Invoices.date.desc()).all()
    return render_template("invoice.html", invoices=invoices_list)

@app.route('/invoice/view/<int:invoice_id>')
@login_required

def invoice_view(invoice_id):
    invoice_obj = Invoices.query.get_or_404(invoice_id)
    return render_template("invoice_view.html", invoice=invoice_obj)


@app.route('/invoice/add', methods=['GET', 'POST'])
@login_required

def invoice_add():
    form = InvoiceForm()
    form.set_vendor_choices()
    pdf_snippet = None

    if form.validate_on_submit():

        existing_invoice = Invoices.query.filter_by(invoice_number=form.invoice_number.data).first()
        if existing_invoice:
            flash('An invoice with this number already exists!')
            return render_template('invoice_add.html', form=form, pdf_snippet=pdf_snippet)
        
        invoice = Invoices(
            invoice_number=form.invoice_number.data,
            date=form.date.data,
            vendor_id=form.vendor_id.data,
            user_id=current_user.id,
            amount=form.amount.data,
            tax=form.tax.data,
            description=form.description.data
        )
        db.session.add(invoice)
        db.session.commit()
        flash("Invoice saved successfully!")
        return redirect(url_for('invoice_add'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "error")

    return render_template('invoice_add.html', form=form, pdf_snippet=pdf_snippet)

# Route to handle AJAX PDF parsing
@app.route('/invoice/parse_pdf', methods=['POST'])
@login_required

def parse_pdf():
    pdf_file = request.files.get('pdf_file')
    if not pdf_file:
        return jsonify({'error': 'No file uploaded.'}), 400
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

    pdf_bytes = pdf_file.read()
    fields, _ = parse_invoice_pdf(pdf_bytes)

    return jsonify({'fields': fields})

@app.route('/invoice/edit/<int:invoice_id>', methods=['GET', 'POST'])
@login_required

def invoice_edit(invoice_id):
    invoice = Invoices.query.get_or_404(invoice_id)
    form = EditInvoiceForm(obj=invoice)
    form.set_vendor_choices()  # populate vendor dropdown

    if form.validate_on_submit():
        invoice.invoice_number = form.invoice_number.data
        invoice.date = form.date.data
        invoice.vendor_id = form.vendor_id.data
        invoice.amount = form.amount.data
        invoice.tax = form.tax.data
        invoice.description = form.description.data

        db.session.commit()
        flash("Invoice updated successfully!")
        # return redirect(url_for('invoice_list'))

    return render_template('invoice_edit.html', form=form, invoice=invoice)

########## Vendors ##########

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

@app.route('/vendor/view/<int:vendor_id>')
@login_required

def vendor_view(vendor_id):
    vendor_obj = Vendors.query.get_or_404(vendor_id)
    return render_template("vendor_view.html", vendor=vendor_obj)

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
        return redirect(url_for('dashboard'))

    return render_template('vendor_add.html', form=form)

@app.route('/vendor/edit/<int:vendor_id>', methods=['GET', 'POST'])
@login_required

def vendor_edit(vendor_id):
    from models import Vendors
    from app import db

    vendor = Vendors.query.get_or_404(vendor_id)

    form = EditVendorForm(obj=vendor)

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

########## Analytics ##########

@app.route("/analytic")
def analytic():
    selected_vendor = request.args.getlist("vendor_id")  # multiple vendors
    vendors = Vendors.query.all()
    
    # Convert to JSON-serializable list of dicts
    vendors_list = [{"id": v.id, "vendor_name": v.vendor_name} for v in vendors]

    bar_data = []

    if selected_vendor:
        vendor_objs = Vendors.query.filter(Vendors.id.in_(selected_vendor)).all()
        for vendor_obj in vendor_objs:
            bar_data.append({
                "vendor": vendor_obj.vendor_name,
                "amount": float(sum([inv.amount for inv in vendor_obj.invoices])),
                "tax": float(sum([inv.tax or 0 for inv in vendor_obj.invoices]))
            })

    return render_template(
        "analytic.html",
        vendors=vendors_list,          # pass the list of dicts
        selected_vendor=selected_vendor,
        bar_data=bar_data
    )

########## Chat Bot ##########

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

@app.route("/chatbot")
@login_required

def chatbot_page():
    conversation = session.get("conversation", [])
    return render_template("chatbot.html", conversation=conversation)

base_prompt = """
You are an expert data assistant and guide for the web application.

You can:
- Answer questions about the database (provided below).
- Help users navigate the site by describing where to find things and what actions are available.
- Format all database responses in **human-readable, friendly style**.
- When asked for a summary or a high-level overview:
    - Provide a concise overview of the app.
    - Focus on main sections, key functionality, and purpose.
    - Do not list individual records or detailed fields.
- When asked to summarize database data (e.g., users, invoices, vendors):
    - Provide numerical summaries such as totals, sums, averages, counts, or other aggregate metrics.
    - Highlight key trends or insights, but avoid listing every individual record.
    - Use human-readable, friendly style with bullets or short sentences.
- When asked to provide lists of records, format them using these examples:
  • John Doe (**Username**: jdoe, **Email**: jdoe@example.com)  
    Account created on 2025-10-25.
  • Global Supplies Inc. (**Business Type**: Wholesale, **Country**: Canada, **City**: Toronto)  
    Created by **ljones** on 2025-10-25.
  • #1001 (**Vendor**: TechMart Solutions, **Amount**: 1250.00, **Tax**: 150.00)  
    Due 2025-11-15.
- Formatting rules:
    - Each record should be summarized as **one bullet point**.
    - Include only the most relevant fields for clarity unless specific fields are requested.
    - Use **bold** for field names; do not use italics or HTML.
    - Separate multiple records with line breaks.
    - Use Markdown bullets for lists.

- For navigation or actions, provide **short, clear step-by-step instructions**.
- For factual questions, respond directly and concisely.
- For casual questions or greetings, respond politely but briefly.
- If data is missing or unknown, respond politely and suggest where the user might find the relevant section of the app.
- Do not dump raw JSON unless explicitly requested.

SITE STRUCTURE & NAVIGATION GUIDE

1. Login Page
   - Users can log in, log in as Guest, create a new user, or reset their password.
   - Visitors can explore freely. They can create a dummy account or log in as a guest user.
   - Any changes are temporary and can be reset from the main page.

2. Dashboard / Main Menu
   - Options available:
     - Invoices
     - Vendors
     - Analytics
     - Ask AI Question (the chatbot)
   - A Reset option is available to restore demo data.
   - Logout button at the bottom.
   - Clicking the username at the top opens the **User Profile**.

3. User Profile
   - Displays: User ID, Username, Email, Account Created, Password Hash.
   - User Actions: View User List, Edit User, Change Password, Logout, Delete User.

4. Invoices Section
   - View a list of all invoices.
   - Click an invoice to view details; option to edit available.
   - Submit a new invoice using one of two options: enter the details manually or upload a PDF to parse it automatically.
   - Download “Standard Invoice PDF (fillable)” as a template.

5. Vendors Section
   - View a list of all vendors.
   - Click a vendor to view details.
   - Click edit to modify vendor details.
   - Create new vendors.

6. Analytics Section
   - View graphs showing total tax and amount for each vendor.

7. Reset Functionality
   - Available from the main page.
   - Restores the app to its default state and re-seeds the database with demo data.
   - Safe to use anytime; helps users start fresh.

CREATOR INFORMATION
- This web application was created by **Tareq Haboukh**.
- LinkedIn: https://www.linkedin.com/in/tareqhaboukh/
- Portfolio: https://tareqhaboukh.github.io/
- Project Github page: https://github.com/Tareqhaboukh/project_one/
"""

@app.route("/ask", methods=["POST"])
@login_required

def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please provide a question."})

    # Initialize or retrieve conversation from session
    if "conversation" not in session:
        session["conversation"] = []

    # Add user's message to session history
    session["conversation"].append({"role": "user", "content": question})

    # Prepare database snapshot
    db_json = table_to_json(limit_per_table=50)
    json_str = json.dumps(db_json)

    # Build prompt dynamically using conversation history
    prompt = f"{base_prompt}\n\nHere is the database:\n{json_str}\n\n"
    for msg in session["conversation"]:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Handle Gemini response structure
        if hasattr(response, "text"):
            answer = response.text.strip()
        elif hasattr(response, "candidates"):
            answer = response.candidates[0].content.strip()
        else:
            answer = str(response)

        # Add assistant's reply to conversation
        session["conversation"].append({"role": "assistant", "content": answer})
        session.modified = True  # ensure the session updates are saved

    except Exception as e:
        answer = f"Error: {str(e)}"

    return jsonify({"answer": answer})

########## Other ##########

@app.route('/reset', methods=['POST', 'GET'])
def reset():
    from data_seed import seed_all

    try:
        # Drop all tables
        db.drop_all()
        db.create_all()

        # Seed database
        seed_all()

        logout_user()

        flash("Database has been reset and demo data reloaded.", "success")
    except Exception as e:
        flash(f"An error occurred while resetting: {str(e)}", "danger")

    return redirect(url_for('index'))


@app.route('/ping')
def ping():
    return 'OK', 200

@app.errorhandler(404)
@login_required

def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
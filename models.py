from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

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

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "date_created": self.date_created.isoformat()
        }
    
class Vendors(db.Model):  
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(120), nullable=False)
    business_type = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Vendor {self.vendor_name}>'
    

class Invoices(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    tax = db.Column(Numeric(10, 2))
    description = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    vendor = db.relationship('Vendors', backref='invoices')
    user = db.relationship('Users', backref='invoices')

    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.vendor.vendor_name}>'
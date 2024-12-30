from models import db, Users

def get_all_users():
    return Users.query.all()

def get_user_by_id(id):
    return Users.query.get_or_404(id)
from models import db, Users

user1 = Users(
    username='jdoe',
    first_name='John',
    last_name='Doe',
    email='jdoe@example.com'
)
user1.hash_password('password')

user2 = Users(
    username='asmith',
    first_name='Anna',
    last_name='Smith',
    email='asmith@example.com'
)
user2.hash_password('password')

user3 = Users(
    username='mbrown',
    first_name='Michael',
    last_name='Brown',
    email='mbrown@example.com'
)
user3.hash_password('password')

user4 = Users(
    username='ljones',
    first_name='Laura',
    last_name='Jones',
    email='ljones@example.com'
)
user4.hash_password('password')

def seed_default_users():
    if Users.query.count() == 0:
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()
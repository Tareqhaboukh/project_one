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
        
    guest_user = Users.query.filter_by(username='guest').first()
    if not guest_user:
        guest_user = Users(
            username='guest',
            first_name='Guest',
            last_name='User',
            email='guest@projectone.com'
        )
        guest_user.hash_password('')
        db.session.add(guest_user)
        db.session.commit()
        print("Guest user created!")

    default_users_count = Users.query.filter(Users.username != 'guest').count()
    if default_users_count == 0:
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()
        print("Default users added!")
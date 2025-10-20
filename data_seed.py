def seed_all():
    seed_default_users()
    seed_default_vendors()

def seed_default_users():
    from app import db
    from models import Users

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

    default_users = [
        {
            "username": "jdoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "jdoe@example.com",
            "password": "password"
        },
        {
            "username": "asmith",
            "first_name": "Anna",
            "last_name": "Smith",
            "email": "asmith@example.com",
            "password": "password"
        },
        {
            "username": "mbrown",
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "mbrown@example.com",
            "password": "password"
        },
        {
            "username": "ljones",
            "first_name": "Laura",
            "last_name": "Jones",
            "email": "ljones@example.com",
            "password": "password"
        },
    ]

    for u in default_users:
        existing = Users.query.filter_by(username=u["username"]).first()
        if not existing:
            user = Users(
                username=u["username"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                email=u["email"]
            )
            user.hash_password(u["password"])
            db.session.add(user)

    db.session.commit()
    print("Default users added!")

def seed_default_vendors():
    from app import db
    from models import Vendors, Users

    users = Users.query.all()
    if not users:
        print("No users found! Please seed users first.")
        return

    vendor_list = [
        Vendors(
            vendor_name="Global Supplies Inc.",
            business_type="Wholesale",
            tax_id="TAX12345",
            country="Canada",
            city="Toronto",
            postal_code="M5H 2N2",
            created_by=users[4].username
        ),
        Vendors(
            vendor_name="TechMart Solutions",
            business_type="IT Services",
            tax_id="TAX54321",
            country="USA",
            city="New York",
            postal_code="10001",
            created_by=users[1].username
        ),
        Vendors(
            vendor_name="GreenLeaf Construction",
            business_type="Construction",
            tax_id="TAX67890",
            country="Canada",
            city="Ottawa",
            postal_code="K1P 5G4",
            created_by=users[2].username
        ),
        Vendors(
            vendor_name="BlueSky Logistics",
            business_type="Transportation",
            tax_id="TAX98765",
            country="UK",
            city="London",
            postal_code="SW1A 1AA",
            created_by=users[3].username
        ),
        Vendors(
            vendor_name="PureWater Systems",
            business_type="Manufacturing",
            tax_id="TAX11223",
            country="Germany",
            city="Berlin",
            postal_code="10115",
            created_by=users[2].username
        ),
    ]

    existing_vendors = Vendors.query.count()
    if existing_vendors == 0:
        db.session.add_all(vendor_list)
        db.session.commit()
        print("Default vendors added!")
    else:
        print("Vendors already exist. Skipping seeding.")
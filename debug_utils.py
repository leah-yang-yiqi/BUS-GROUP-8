from app import app, db, User, Admin, Student

from werkzeug.security import generate_password_hash


def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        users = [
            Admin(username='amy', password_hash=generate_password_hash('amy.pw'), role='Admin', type='admin',
                  permissions='full_access'),
            Student(username='tom', password_hash=generate_password_hash('tom.pw'), role='Student', type='student',
                    major='Computer Science', year=2025),
            User(username='yin', password_hash=generate_password_hash('yin.pw'), role='Staff', type='user'),
        ]

        db.session.add_all(users)
        db.session.commit()
        print("database input successfully")


if __name__ == "__main__":
    reset_db()

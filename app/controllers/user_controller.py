from app.models.user_model import User
from app.extensions import db
from app.models.user_model import UserRole
import app.errors as errors
def get_all_users():
    return [user.to_dict() for user in User.query.all()]

def get_user_by_id(user_id):
    user = User.query.get(user_id)
    return user.to_dict() if user else None

def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user.to_dict() if user else None

def create_user(username, email, password="changeme", role=UserRole.USER):
    if User.query.filter_by(email=email).first():
        raise errors.UserAlreadyExistsError("User with this email already exists.")
    if User.query.filter_by(username=username).first():
        raise errors.UserAlreadyExistsError("User with this username already exists.")
    user = User(username=username, email=email, password="temp", role=role)
    
    try:
        user.set_password(raw_password=password)
    except Exception as e:
        raise errors.AppError(f"Failed to set password: {str(e)}")
    db.session.add(user)
    db.session.commit()
    
    return user.to_dict()

def update_user(user_id, username, email):
    user = User.query.get(user_id)
    if user:
        user.username = username
        user.email = email
        db.session.commit()
        return user.to_dict()
    return None

def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

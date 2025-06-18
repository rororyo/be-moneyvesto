from app.extensions import db
import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID,ENUM
from datetime import datetime,timezone
from argon2 import PasswordHasher

ph = PasswordHasher()
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Integer, nullable=True, default=0)
    role = db.Column(ENUM(UserRole), nullable=False, default=UserRole.USER)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, raw_password):
        self.password = ph.hash(raw_password)

    def check_password(self, raw_password):
        try:
            return ph.verify(self.password, raw_password)
        except Exception:
            return False
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'role': self.role.value,
            'balance': self.balance,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
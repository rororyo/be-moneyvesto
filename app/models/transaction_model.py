from app.extensions import db
import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID,ENUM
from datetime import datetime,timezone
class TransactionType(enum.Enum):
  DEPOSIT = "deposit"
  WITHDRAWAL = "withdrawal"

class Transaction(db.Model):
  __tablename__ = "transactions"

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
  description = db.Column(db.String(100), nullable=False)
  transaction_type = db.Column(ENUM(TransactionType), nullable=False)
  amount = db.Column(db.Integer, nullable=False)
  total_price = db.Column(db.Float, nullable=False)
  created_at = db.Column(db.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at = db.Column(db.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
  user = db.relationship('User', back_populates='transactions')

  def to_dict(self):
      return {
          'id': str(self.id),
          'description': self.description,
          'transaction_type': self.transaction_type.value,
          'amount': self.amount,
          'total_price': self.total_price,
          'created_at': self.created_at,
          'updated_at': self.updated_at,
          'user': self.user.to_dict() if self.user else None
      }
from app.models.transaction_model import Transaction,TransactionType
from app.extensions import db
import app.errors as errors
def get_all_transactions():
    return [transaction.to_dict() for transaction in Transaction.query.all()]

def get_transaction_by_id(transaction_id):
    transaction = db.session.query(Transaction).filter_by(id=transaction_id).first()
    return transaction.to_dict() if transaction else None

def create_transaction(user_id, description, transaction_type, amount, total_price):
    transaction = Transaction(user_id=user_id, description=description, transaction_type=transaction_type, amount=amount, total_price=total_price)
    db.session.add(transaction)
    db.session.commit()
    return transaction.to_dict()

def update_transaction(transaction_id,description, transaction_type, amount, total_price):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        transaction.description = description
        transaction.transaction_type = transaction_type
        transaction.amount = amount
        transaction.total_price = total_price
        db.session.commit()
        return transaction.to_dict()
    return None

def delete_transaction(transaction_id):
    
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        return True
    return False
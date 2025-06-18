from app.models.transaction_model import Transaction,TransactionType
from app.models.user_model import User
from app.extensions import db
import app.errors as errors
from flask import request
from sqlalchemy import extract, asc, desc
def get_all_transactions():
    page = request.args.get('page', default=1, type=int)
    size = request.args.get('size', default=10, type=int)
    created_month = request.args.get('created_month')  # format: YYYY-MM
    description = request.args.get('description')
    transaction_type = request.args.get('transaction_type')
    user_id = request.args.get('user_id')
    order = request.args.get('order', 'asc')  # default to ascending

    query = Transaction.query

    if created_month:
        try:
            year, month = map(int, created_month.split("-"))
            query = query.filter(
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            )
        except ValueError:
            pass  # Skip invalid date filters silently

    if description:
        query = query.filter(Transaction.description.ilike(f'%{description}%'))

    if transaction_type:
        if transaction_type == 'deposit':
            transaction_type = TransactionType.DEPOSIT
        elif transaction_type == 'withdrawal':
            transaction_type = TransactionType.WITHDRAWAL
        else:
            transaction_type = None
        query = query.filter(Transaction.transaction_type == transaction_type)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)

    if order == 'desc':
        query = query.order_by(desc(Transaction.total_price))
    else:
        query = query.order_by(asc(Transaction.total_price))

    pagination = query.paginate(page=page, per_page=size, error_out=False)

    return {
        "data": [t.to_dict() for t in pagination.items],
        "paging": {
            "page": pagination.page,
            "size": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }
    }

def get_transaction_by_id(transaction_id):
    transaction = db.session.query(Transaction).filter_by(id=transaction_id).first()
    return transaction.to_dict() if transaction else None

def update_user_balance(user_id):
    """Calculate and update user's balance based on all their transactions"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Calculate total balance from all transactions
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    balance = 0
    
    for transaction in transactions:
        if transaction.transaction_type == TransactionType.DEPOSIT:
            balance += transaction.total_price
        elif transaction.transaction_type == TransactionType.WITHDRAWAL:
            balance -= transaction.total_price
    
    user.balance = balance
    db.session.commit()
    return True

def create_transaction(user_id, description, transaction_type, amount, total_price):
    transaction = Transaction(
        user_id=user_id, 
        description=description, 
        transaction_type=transaction_type, 
        amount=amount, 
        total_price=total_price
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Update user balance after creating transaction
    update_user_balance(user_id)
    
    return transaction.to_dict()

def create_multiple_transactions(user_id, transactions_data):
    """Create multiple transactions in a single database transaction"""
    transactions = []
    for transaction_data in transactions_data:
        transaction_type = transaction_data['transaction_type']
        if transaction_type == 'withdrawal':
            transaction_type = TransactionType.WITHDRAWAL
        elif transaction_type == 'deposit':
            transaction_type = TransactionType.DEPOSIT
            
        transaction = Transaction(
            user_id=user_id,
            description=transaction_data['description'],
            transaction_type=transaction_type,
            amount=transaction_data['amount'],
            total_price=transaction_data['total_price']
        )
        db.session.add(transaction)
        transactions.append(transaction)
    
    db.session.commit()
    
    # Update user balance after creating all transactions
    update_user_balance(user_id)
    
    return [transaction.to_dict() for transaction in transactions]

def update_transaction(transaction_id, description, transaction_type, amount, total_price):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        user_id = transaction.user_id  # Store user_id before updating
        
        transaction.description = description
        transaction.transaction_type = transaction_type
        transaction.amount = amount
        transaction.total_price = total_price
        db.session.commit()
        
        # Update user balance after updating transaction
        update_user_balance(user_id)
        
        return transaction.to_dict()
    return None

def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        user_id = transaction.user_id  # Store user_id before deleting
        
        db.session.delete(transaction)
        db.session.commit()
        
        # Update user balance after deleting transaction
        update_user_balance(user_id)
        
        return True
    return False
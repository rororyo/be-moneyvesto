from flask import Blueprint, jsonify, request, make_response
from app.controllers.transaction_controller import get_all_transactions, get_transaction_by_id,create_transaction, create_multiple_transactions, update_transaction, delete_transaction
import app.errors as errors
from app.models.transaction_model import Transaction,TransactionType
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['GET'])
def fetch_transactions():
    return jsonify(get_all_transactions())

@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def save_transaction():
    data = request.get_json()
    print(data)
    user_id = get_jwt_identity()
    
    # Check if data is a list (multiple transactions) or dict (single transaction)
    if isinstance(data, list):
        # Handle multiple transactions
        if not data:
            return jsonify({'message': 'Transaction list cannot be empty'}), 400
            
        # Validate each transaction in the list
        for i, transaction_data in enumerate(data):
            # Check required fields
            required_fields = ['transaction_type', 'description', 'amount', 'total_price']
            for field in required_fields:
                if field not in transaction_data:
                    return jsonify({'message': f'Missing {field} in transaction {i+1}'}), 400
            
            # Validate transaction type
            if transaction_data['transaction_type'] not in ['deposit', 'withdrawal']:
                return jsonify({'message': f'Invalid transaction type in transaction {i+1}'}), 400
        
        # Create multiple transactions
        try:
            transactions = create_multiple_transactions(user_id, data)
            return jsonify({
                'message': f'Successfully created {len(transactions)} transactions',
                'transactions': transactions
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to create transactions', 'error': str(e)}), 500
            
    else:
        # Handle single transaction (existing logic)
        required_fields = ['transaction_type', 'description', 'amount', 'total_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing {field}'}), 400
                
        transaction_type = data['transaction_type']
        if transaction_type not in ['deposit', 'withdrawal']:
            return jsonify({'message': 'Invalid transaction type'}), 400
            
        if transaction_type == 'withdrawal':
            transaction_type = TransactionType.WITHDRAWAL
        if transaction_type == 'deposit':
            transaction_type = TransactionType.DEPOSIT
            
        try:
            transaction = create_transaction(
                user_id=user_id,
                description=data['description'],
                transaction_type=transaction_type,
                amount=data['amount'],
                total_price=data['total_price']
            )
            return jsonify(transaction), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to create transaction', 'error': str(e)}), 500

@transaction_bp.route('/<transaction_id>', methods=['GET'])
def fetch_transaction(transaction_id):
    transaction = get_transaction_by_id(transaction_id=transaction_id)
    if transaction:
        return jsonify(transaction)
    return jsonify({'message': 'transaction not found'}), 404

@transaction_bp.route('/<transaction_id>', methods=['PUT'])
def modify_transaction(transaction_id):
    data = request.get_json()
    transaction_type = data['transaction_type']
    if transaction_type not in ['deposit', 'withdrawal']:
        return jsonify({'message': 'Invalid transaction type'}), 400
    if transaction_type == 'withdrawal':
        transaction_type = TransactionType.WITHDRAWAL
    if transaction_type == 'deposit':
        transaction_type = TransactionType.DEPOSIT
    transaction = update_transaction(transaction_id=transaction_id, description=data['description'], transaction_type=transaction_type, amount=data['amount'], total_price=data['total_price'])
    if transaction:
        return jsonify(transaction), 200
    return jsonify({'message': 'transaction not found'}), 404


@transaction_bp.route('/<transaction_id>', methods=['DELETE'])
def remove_transaction(transaction_id):
    success = delete_transaction(transaction_id=transaction_id)
    if success:
        return jsonify({'message': 'transaction deleted'}), 200
    return jsonify({'message': 'transaction not found'}), 404
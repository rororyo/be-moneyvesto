from flask import Blueprint, jsonify, request, make_response
from app.controllers.transaction_controller import get_all_transactions, get_transaction_by_id,create_transaction
import app.errors as errors
from app.models.transaction_model import Transaction,TransactionType
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['GET'])
def fetch_transactions():
    return jsonify(get_all_transactions())

@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def save_transaction():
    data = request.get_json()
    user_id = get_jwt_identity()
    transaction_type = data['transaction_type']
    if transaction_type not in ['deposit', 'withdrawal']:
        return jsonify({'message': 'Invalid transaction type'}), 400
    if transaction_type == 'withdrawal':
        transaction_type = TransactionType.WITHDRAWAL
    if transaction_type == 'deposit':
        transaction_type = TransactionType.DEPOSIT
    transaction = create_transaction(user_id=user_id, description=data['description'], transaction_type=transaction_type, amount=data['amount'], total_price=data['total_price'])
    return jsonify(transaction), 201

@transaction_bp.route('/<transaction_id>', methods=['GET'])
def fetch_transaction(transaction_id):
    transaction = get_transaction_by_id(transaction_id=transaction_id)
    if transaction:
        return jsonify(transaction)
    return jsonify({'message': 'transaction not found'}), 404


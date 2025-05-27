from flask import Blueprint, jsonify, request, make_response
from app.controllers.user_controller import (
    get_all_users, get_user_by_id, create_user, update_user, delete_user
)
import app.errors as errors
from app.models.user_model import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
def fetch_users():
    return jsonify(get_all_users())

@user_bp.route('/<user_id>', methods=['GET'])
def fetch_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    return jsonify({'message': 'User not found'}), 404

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(msg='User not found'), 404
    return jsonify(user.to_dict()), 200

@user_bp.route('/register', methods=['POST'])
def handle_register():
    data = request.get_json()
    try:
        new_user = create_user(data['username'], data['email'],data['password'])
        return jsonify(new_user), 201
    except errors.UserAlreadyExistsError as e:
        return jsonify({'error': str(e)}), 409
    except errors.AppError as e:
        return jsonify({'error': str(e)}), 500
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    identifier = data.get('identifier')  # Can be username or email
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'msg': 'Missing credentials'}), 400

    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()

    if not user or not user.check_password(password):
        return jsonify({'msg': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    return jsonify({'access_token': access_token}), 200

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = make_response(jsonify({
        'msg': 'Logout success'
    }))
    
    # Clear cookie named "token"
    response.set_cookie(
        'token',
        '',
        expires=0,
        httponly=True,
        secure=False, 
        samesite='Lax'
    )
    
    return response

@user_bp.route('/<user_id>', methods=['PUT'])
def modify_user(user_id):
    data = request.get_json()
    user = update_user(user_id, data['username'], data['email'])
    if user:
        return jsonify(user)
    return jsonify({'message': 'User not found'}), 404

@user_bp.route('/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    success = delete_user(user_id)
    if success:
        return jsonify({'message': 'User deleted'})
    return jsonify({'message': 'User not found'}), 404

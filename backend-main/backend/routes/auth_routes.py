from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.user_service import UserService
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
user_service = UserService()


@auth_bp.route('/login-hybrid', methods=['POST'])
def login_hybrid():
    """
    HYBRID LOGIN: Automatically chooses best authentication method
    
    - CSV users (user1, user2, user3) → Use ML Model (95% accuracy)
    - New DB users (alice, bob, etc.) → Use Database Comparison (75-85% accuracy)
    
    Request body:
        {
            "username": "string",
            "keystroke_features_list": [
                { ks_count, ks_rate, dwell_mean, ... },  # Sentence 1
                { ks_count, ks_rate, dwell_mean, ... }   # Sentence 2
            ]
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        username = data.get('username')
        keystroke_features_list = data.get('keystroke_features_list')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        if not keystroke_features_list or len(keystroke_features_list) != 2:
            return jsonify({'error': 'Exactly 2 keystroke feature sets required'}), 400
        
        print(f"\n🔐 HYBRID LOGIN for user: {username}")
        
        # Check if user exists
        user = user_service.find_user_by_name(username)
        if not user:
            return jsonify({
                'access_granted': False,
                'error': 'User not found'
            }), 404
        
        # Authenticate using hybrid system
        result = auth_service.authenticate_hybrid(
            username=username,
            keystroke_features_list=keystroke_features_list
        )
        
        if result['access_granted']:
            return jsonify({
                'access_granted': True,
                'username': username,
                'method': result['method'],
                'confidence': result.get('confidence'),
                'similarity': result.get('similarity'),
                'message': result['message'],
                'user_id': user['user_id']
            }), 200
        else:
            return jsonify({
                'access_granted': False,
                'username': username,
                'method': result['method'],
                'predicted_user': result.get('predicted_user'),
                'confidence': result.get('confidence'),
                'similarity': result.get('similarity'),
                'error': result['message']
            }), 401
    
    except Exception as e:
        print(f"❌ Hybrid login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'access_granted': False,
            'error': 'Authentication failed'
        }), 401


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    LEGACY LOGIN: XGBoost prediction only (for CSV users)
    Kept for backward compatibility
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        username = data.get('username')
        keystroke_features_list = data.get('keystroke_features_list')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        if not keystroke_features_list:
            return jsonify({'error': 'Keystroke features required'}), 400
        
        # Authenticate using ML model only
        predicted_user, confidence = auth_service.predict_user_from_keystroke(
            keystroke_features_list
        )
        
        if predicted_user.lower() == username.lower():
            return jsonify({
                'access_granted': True,
                'predicted_user': predicted_user,
                'entered_user': username,
                'confidence': confidence,
                'message': 'Login successful',
                'user_id': user_service.find_user_by_name(username)['user_id']
            }), 200
        else:
            return jsonify({
                'access_granted': False,
                'predicted_user': predicted_user,
                'entered_user': username,
                'confidence': confidence,
                'error': 'Typing pattern does not match'
            }), 401
    
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({
            'access_granted': False,
            'error': 'Authentication failed'
        }), 401


@auth_bp.route('/login-password', methods=['POST'])
def login_password():
    """
    PASSWORD LOGIN: Traditional authentication
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        print(f"🔍 Password login attempt - Username: '{username}'")
        
        if not username or not password:
            return jsonify({
                'error': 'Username and password are required',
                'access_granted': False
            }), 400
        
        # Find user
        user = user_service.find_user_by_name(username)
        
        if not user:
            print(f"❌ User not found: {username}")
            return jsonify({
                'error': 'User not found',
                'access_granted': False
            }), 404
        
        # Verify password
        if user_service.verify_password(user['user_id'], password):
            print(f"✅ Password verified for user: {username}")
            return jsonify({
                'access_granted': True,
                'username': user['name'],
                'user_id': user['user_id'],
                'message': 'Login successful'
            }), 200
        else:
            print(f"❌ Invalid password for user: {username}")
            return jsonify({
                'error': 'Invalid password',
                'access_granted': False
            }), 401
    
    except Exception as e:
        print(f"❌ Password login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'access_granted': False,
            'error': 'Authentication failed'
        }), 401
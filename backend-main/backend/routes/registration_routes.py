"""
Registration routes for user registration with keystroke enrollment.
Saves 5 keystroke samples to database (not CSV).
"""
from flask import Blueprint, request, jsonify
from services.user_service import UserService

registration_bp = Blueprint('registration', __name__)
user_service = UserService()


@registration_bp.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user with keystroke biometric enrollment.
    Collects 5 typing samples and saves ONLY to database.

    Request body:
        {
            "name": "string",
            "email": "string",
            "role": "student|teacher|admin",
            "password": "string",
            "keystroke_features": {
                "ks_count": number,
                "ks_rate": number,
                "dwell_mean": number,
                "dwell_std": number,
                "flight_mean": number,
                "flight_std": number,
                "digraph_mean": number,
                "digraph_std": number,
                "backspace_rate": number,
                "wps": number,
                "wpm": number
            },
            "attempt": 1|2|3|4|5
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        name = data.get('name')
        email = data.get('email')
        role = data.get('role', 'student')
        password = data.get('password')
        keystroke_features = data.get('keystroke_features')
        attempt = data.get('attempt', 1)

        # Validate required fields
        if not all([name, email, password, keystroke_features]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate attempt number
        if attempt not in [1, 2, 3, 4, 5]:
            return jsonify({'error': 'Invalid attempt number (must be 1-5)'}), 400

        # On first attempt, create user and hash password
        if attempt == 1:
            print(f"\n🆕 Creating new user: {name}")
            
            # Check if user already exists
            existing_user = user_service.find_user_by_name(name)
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
            
            # Create user
            user = user_service.create_user(name, email)
            if not user:
                return jsonify({'error': 'Failed to create user'}), 500
            
            user_id = user['user_id']
            
            # Hash and save password
            user_service.save_password(user_id, password)
            
            print(f"✅ Created user_id: {user_id}")
        else:
            # Find existing user for subsequent attempts
            user = user_service.find_user_by_name(name)
            if not user:
                return jsonify({'error': 'User not found for subsequent attempts'}), 404
            user_id = user['user_id']

        # Save keystroke profile to DATABASE
        reg_id = user_id  # Use user_id as reg_id
        sample_text = f"Registration attempt {attempt}"
        
        success = user_service.save_keystroke_profile(
            user_id=user_id,
            reg_id=reg_id,
            sample_text=sample_text,
            typing_pattern=keystroke_features
        )
        
        if not success:
            return jsonify({'error': 'Failed to save keystroke profile'}), 500
        
        print(f"✅ Saved keystroke profile for {name} (attempt {attempt}/5) to DATABASE")

        return jsonify({
            'message': f'Keystroke data saved (attempt {attempt}/5)',
            'user_id': user_id,
            'attempt': attempt,
            'total_attempts': 5
        }), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
"""
Flask Backend for Typing Biometric Authentication
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.auth_service import AuthService
from services.user_service import UserService

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize services
auth_service = AuthService()
user_service = UserService()

print("Starting TypeID Backend")


@app.route('/api/register', methods=['POST'])
def register():
    """Register endpoint - saves keystroke samples to database"""
    try:
        data = request.get_json()
        
        # DEBUG: Print what we received
        print(f"\n{'='*60}")
        print(f"📥 REGISTRATION REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"Full data: {data}")
        print(f"Username: {data.get('name')}")
        print(f"Email: {data.get('email')}")
        print(f"Keystroke features type: {type(data.get('keystroke_features'))}")
        print(f"Keystroke features: {data.get('keystroke_features')}")
        print(f"Sample text: {data.get('sample_text')}")
        print(f"Attempt number: {data.get('attempt')}")
        print(f"{'='*60}\n")
        
        # Get data - frontend sends 'name', not 'username'
        username = data.get('name') or data.get('username')
        email = data.get('email')
        keystroke_features = data.get('keystroke_features')
        sample_text = data.get('sample_text', 'The quick brown fox jumps over the lazy dog')
        attempt_number = data.get('attempt', 1)
        
        if not username or not email or not keystroke_features:
            return jsonify({
                'success': False,
                'message': 'Username, email, and keystroke features are required'
            }), 400
        
        # Check if user exists, if not create
        user = user_service.find_user_by_name(username)
        if not user:
            print(f"🆕 Creating new user: {username}")
            user = user_service.create_user(username, email)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create user'
                }), 500
        
        user_id = user.get('user_id') or user.get('id')
        
        # Save keystroke profile
        success = user_service.save_keystroke_profile(
            user_id=user_id,
            reg_id=user_id,  # You can generate a separate reg_id if needed
            sample_text=sample_text,
            typing_pattern=keystroke_features
        )
        
        if success:
            print(f"✅ Saved keystroke profile for {username} (attempt {attempt_number}) to DATABASE")
            return jsonify({
                'success': True,
                'message': f'Sample {attempt_number} registered successfully',
                'user_id': user_id,
                'attempt': attempt_number
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save keystroke profile'
            }), 500
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/login-password', methods=['POST'])
def login_password():
    """
    Traditional password-based login (no biometric authentication)
    """
    try:
        data = request.get_json()
        username = data.get('name') or data.get('username')
        password = data.get('password')
        
        print(f"\n{'='*60}")
        print(f"🔑 PASSWORD LOGIN ATTEMPT for user: {username}")
        print(f"{'='*60}")
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Simple check - just verify user exists
        # You can add password hashing/verification here later
        user = user_service.find_user_by_name(username)
        
        if user:
            print(f"✅ Password login successful for {username}")
            
            # Record login session
            user_id = user.get('user_id') or user.get('id')
            user_service.create_login_session(
                user_id=user_id,
                reg_id=user_id,
                login_method='password',
                status='success'
            )
            
            response_data = {
                'access_granted': True,  # Frontend expects this
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'user_id': user_id,
                    'email': user.get('email')
                }
            }
            print(f"📤 Sending response: {response_data}")
            return jsonify(response_data), 200
        else:
            print(f"❌ User not found: {username}")
            
            # Record failed login attempt
            user_service.create_login_session(
                user_id=0,  # Unknown user
                reg_id=0,
                login_method='password',
                status='failed'
            )
            
            return jsonify({
                'access_granted': False,  # Frontend expects this
                'success': False,
                'error': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        print(f"❌ Password login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint with two-layer authentication:
    1. Statistical matching against 3 database samples
    2. ML model prediction from 100-sample trained model
    """
    try:
        data = request.get_json()
        username = data.get('name') or data.get('username')
        # Handle both 'keystroke_features' and 'keystroke_features_list' from frontend
        keystroke_features = data.get('keystroke_features') or data.get('keystroke_features_list', [])
        
        print(f"\n{'='*60}")
        print(f"🔐 LOGIN ATTEMPT for user: {username}")
        print(f"{'='*60}")
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        if not keystroke_features:
            return jsonify({
                'success': False,
                'message': 'Keystroke data is required'
            }), 400
        
        # Validate keystroke features have required fields
        required_fields = ['ks_count', 'ks_rate', 'dwell_mean', 'dwell_std', 
                          'flight_mean', 'flight_std', 'digraph_mean', 
                          'digraph_std', 'backspace_rate', 'wps', 'wpm']
        
        if isinstance(keystroke_features, list):
            sample = keystroke_features[0] if keystroke_features else {}
        else:
            sample = keystroke_features
        
        missing_fields = [f for f in required_fields if f not in sample]
        if missing_fields:
            print(f"⚠️ Missing fields: {missing_fields}")
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # TWO-LAYER AUTHENTICATION
        auth_result = auth_service.authenticate_user(username, keystroke_features)
        
        if auth_result['authenticated']:
            print(f"\n{'='*60}")
            print(f"✅ LOGIN SUCCESSFUL for user: {username}")
            print(f"{'='*60}\n")
            
            # Record successful biometric login session
            user_id = auth_result['user'].get('user_id') or auth_result['user'].get('id')
            user_service.create_login_session(
                user_id=user_id,
                reg_id=user_id,
                login_method='biometric',
                status='success'
            )
            
            # Convert all boolean/numpy types to native Python types for JSON serialization
            details = auth_result['details']
            if details:
                details = {
                    'statistical_match': {
                        'score': float(details['statistical_match']['score']),
                        'passed': bool(details['statistical_match']['passed']),
                        'threshold': float(details['statistical_match']['threshold'])
                    },
                    'ml_prediction': {
                        'predicted_user': str(details['ml_prediction']['predicted_user']),
                        'confidence': float(details['ml_prediction']['confidence']),
                        'user_match': bool(details['ml_prediction']['user_match']),
                        'confidence_pass': bool(details['ml_prediction']['confidence_pass']),
                        'passed': bool(details['ml_prediction']['passed']),
                        'threshold': float(details['ml_prediction']['threshold'])
                    }
                }
            
            return jsonify({
                'access_granted': True,  # Frontend expects this
                'success': True,
                'predicted_user': username,  # Frontend expects this
                'message': auth_result['message'],
                'user': {
                    'username': username,
                    'user_id': user_id
                },
                'authentication_details': details
            }), 200
        else:
            print(f"\n{'='*60}")
            print(f"❌ LOGIN FAILED for user: {username}")
            print(f"   Reason: {auth_result['message']}")
            print(f"{'='*60}\n")
            
            # Record failed biometric login attempt
            user = user_service.find_user_by_name(username)
            user_id = user.get('user_id') if user else 0
            user_service.create_login_session(
                user_id=user_id,
                reg_id=user_id if user else 0,
                login_method='biometric',
                status='failed'
            )
            
            # Get the predicted user from ML model
            predicted_user = auth_result['details']['ml_prediction']['predicted_user'] if auth_result['details'] else 'unknown'
            
            # Convert all boolean/numpy types to native Python types for JSON serialization
            details = auth_result['details']
            if details:
                details = {
                    'statistical_match': {
                        'score': float(details['statistical_match']['score']),
                        'passed': bool(details['statistical_match']['passed']),
                        'threshold': float(details['statistical_match']['threshold'])
                    },
                    'ml_prediction': {
                        'predicted_user': str(details['ml_prediction']['predicted_user']),
                        'confidence': float(details['ml_prediction']['confidence']),
                        'user_match': bool(details['ml_prediction']['user_match']),
                        'confidence_pass': bool(details['ml_prediction']['confidence_pass']),
                        'passed': bool(details['ml_prediction']['passed']),
                        'threshold': float(details['ml_prediction']['threshold'])
                    }
                }
            
            return jsonify({
                'access_granted': False,  # Frontend expects this
                'success': False,
                'predicted_user': predicted_user,  # Frontend expects this
                'message': auth_result['message'],
                'authentication_details': details
            }), 401
            
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ LOGIN ERROR: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': 'Internal server error during authentication'
        }), 500


@app.route('/api/login-hybrid', methods=['POST', 'OPTIONS'])
def login_hybrid():
    """
    Hybrid login endpoint with intelligent routing:
    - CSV users (user1, user2, user3) → ML Model (95% accuracy)
    - Database-only users → Statistical comparison (75-85% accuracy)
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        username = data.get('username') or data.get('name')
        keystroke_features_list = data.get('keystroke_features_list', [])
        
        print(f"\n{'='*60}")
        print(f"🔐 HYBRID LOGIN ATTEMPT for user: {username}")
        print(f"Number of keystroke samples: {len(keystroke_features_list)}")
        print(f"{'='*60}")
        
        if not username:
            return jsonify({
                'access_granted': False,
                'message': 'Username is required'
            }), 400
        
        if not keystroke_features_list or len(keystroke_features_list) == 0:
            return jsonify({
                'access_granted': False,
                'message': 'Keystroke features are required'
            }), 400
        
        # Step 1: Check if user exists in database
        user = user_service.find_user_by_name(username)
        
        if not user:
            print(f"❌ User '{username}' not found in database")
            return jsonify({
                'access_granted': False,
                'message': 'User not found'
            }), 404
        
        user_id = user.get('user_id') or user.get('id')
        
        # Step 2: Check if user is in CSV/ML Model
        csv_users = ['user1', 'user2', 'user3']  # Users with 100 samples in CSV
        
        if username in csv_users:
            # HIGH ACCURACY PATH: Use ML Model (95% accuracy)
            print(f"✅ User '{username}' found in CSV - Using ML MODEL (High Accuracy)")
            
            try:
                # Use the existing auth_service which has ML model logic
                # Pass the first sample for compatibility (or modify auth_service to handle lists)
                auth_result = auth_service.authenticate_user(username, keystroke_features_list)
                
                if auth_result['authenticated']:
                    ml_details = auth_result['details']['ml_prediction']
                    
                    # Record successful login
                    user_service.create_login_session(
                        user_id=user_id,
                        reg_id=user_id,
                        login_method='ml_model',
                        status='success'
                    )
                    
                    return jsonify({
                        'access_granted': True,
                        'username': username,
                        'method': 'ML_MODEL',
                        'confidence': float(ml_details['confidence']),
                        'message': 'Login successful (High accuracy - ML Model)',
                        'details': {
                            'predicted_user': str(ml_details['predicted_user']),
                            'confidence': float(ml_details['confidence']),
                            'threshold': float(ml_details['threshold'])
                        }
                    }), 200
                else:
                    # ML model rejected
                    ml_details = auth_result['details']['ml_prediction']
                    
                    # Record failed login
                    user_service.create_login_session(
                        user_id=user_id,
                        reg_id=user_id,
                        login_method='ml_model',
                        status='failed'
                    )
                    
                    return jsonify({
                        'access_granted': False,
                        'username': username,
                        'method': 'ML_MODEL',
                        'message': 'Authentication failed - Typing pattern does not match',
                        'details': {
                            'predicted_user': str(ml_details['predicted_user']),
                            'confidence': float(ml_details['confidence']),
                            'threshold': float(ml_details['threshold'])
                        }
                    }), 401
                    
            except Exception as e:
                print(f"❌ ML Model error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'access_granted': False,
                    'message': f'ML Model authentication failed: {str(e)}'
                }), 500
        
        else:
            # FAST PATH: Use Database Comparison (75-85% accuracy)
            print(f"✅ User '{username}' NOT in CSV - Using DATABASE COMPARISON (Fast Path)")
            
            try:
                # Use existing auth_service for statistical matching
                auth_result = auth_service.authenticate_user(username, keystroke_features_list)
                
                if auth_result['authenticated']:
                    stat_details = auth_result['details']['statistical_match']
                    
                    # Record successful login
                    user_service.create_login_session(
                        user_id=user_id,
                        reg_id=user_id,
                        login_method='database_comparison',
                        status='success'
                    )
                    
                    return jsonify({
                        'access_granted': True,
                        'username': username,
                        'method': 'DATABASE_COMPARISON',
                        'similarity': float(stat_details['score']),
                        'message': 'Login successful (Database profile match)',
                        'details': {
                            'similarity': float(stat_details['score']),
                            'threshold': float(stat_details['threshold'])
                        }
                    }), 200
                else:
                    # Statistical matching failed
                    stat_details = auth_result['details']['statistical_match']
                    
                    # Record failed login
                    user_service.create_login_session(
                        user_id=user_id,
                        reg_id=user_id,
                        login_method='database_comparison',
                        status='failed'
                    )
                    
                    return jsonify({
                        'access_granted': False,
                        'username': username,
                        'method': 'DATABASE_COMPARISON',
                        'message': 'Authentication failed - Typing pattern does not match stored profile',
                        'details': {
                            'similarity': float(stat_details['score']),
                            'threshold': float(stat_details['threshold'])
                        }
                    }), 401
                    
            except Exception as e:
                print(f"❌ Database comparison error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'access_granted': False,
                    'message': f'Database comparison failed: {str(e)}'
                }), 500
            
    except Exception as e:
        print(f"❌ Hybrid login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'access_granted': False,
            'message': 'Internal server error during authentication'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'TypeID Backend is running'
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
User service for managing user data
"""
import sqlite3
import json
from datetime import datetime

def get_db_connection():
    """Get database connection with timeout to prevent locking"""
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'biometric_app.db')
    conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None)  # Increased timeout, autocommit mode
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent access
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


class UserService:
    """Service for user operations"""
    
    def __init__(self):
        # Don't store connection - create fresh one for each operation
        pass
    
    def _get_conn(self):
        """Get a fresh database connection for each operation"""
        return get_db_connection()
    
    def find_user_by_name(self, username):
        """Find user by username"""
        conn = self._get_conn()
        try:
            query = "SELECT * FROM user WHERE name = ?"
            cursor = conn.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"❌ Error finding user: {e}")
            return None
        finally:
            conn.close()
    
    def find_user_by_id(self, user_id):
        """Find user by user_id"""
        conn = self._get_conn()
        try:
            query = "SELECT * FROM user WHERE user_id = ?"
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"❌ Error finding user: {e}")
            return None
        finally:
            conn.close()
    
    def create_user(self, name, email):
        """Create a new user"""
        conn = self._get_conn()
        try:
            # First create user in user table
            query = """
            INSERT INTO user (name, email, created_at)
            VALUES (?, ?, ?)
            """
            cursor = conn.execute(query, (name, email, datetime.now().isoformat()))
            
            user_id = cursor.lastrowid
            user = self.find_user_by_id(user_id)
            
            # Also create entry in user_registration table
            if user:
                self.create_user_registration(user_id)
            
            return user
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
        finally:
            conn.close()
    
    def create_user_registration(self, user_id):
        """Create user registration record"""
        conn = self._get_conn()
        try:
            query = """
            INSERT INTO user_registration (reg_id, user_id, password, biometriclogin, registration_date)
            VALUES (?, ?, ?, ?, ?)
            """
            # Use user_id as reg_id for simplicity
            conn.execute(query, (
                user_id,  # reg_id
                user_id,  # user_id
                'hashed_password_placeholder',  # password (can be updated later)
                'enabled',  # biometriclogin
                datetime.now().isoformat()
            ))
            print(f"✅ Created user_registration record for user_id {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error creating user_registration: {e}")
            return False
        finally:
            conn.close()
    
    def create_login_session(self, user_id, reg_id, login_method='biometric', status='success'):
        """Create login session record"""
        conn = self._get_conn()
        try:
            query = """
            INSERT INTO login_session (user_id, reg_id, login_time, status, login_method)
            VALUES (?, ?, ?, ?, ?)
            """
            conn.execute(query, (
                user_id,
                reg_id,
                datetime.now().isoformat(),
                status,
                login_method
            ))
            print(f"✅ Created login_session record for user_id {user_id} ({login_method}, {status})")
            return True
        except Exception as e:
            print(f"❌ Error creating login_session: {e}")
            return False
        finally:
            conn.close()
    
    def save_keystroke_profile(self, user_id, reg_id, sample_text, typing_pattern):
        """Save keystroke profile to biometric_profile table"""
        conn = None
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self._get_conn()
                
                query = """
                INSERT INTO biometric_profile (user_id, reg_id, sample_text, typing_pattern, created_date)
                VALUES (?, ?, ?, ?, ?)
                """
                
                # Convert typing_pattern dict to JSON string
                typing_pattern_json = json.dumps(typing_pattern)
                
                conn.execute(query, (
                    user_id,
                    reg_id,
                    sample_text,
                    typing_pattern_json,
                    datetime.now().isoformat()
                ))
                
                print(f"✅ Successfully saved keystroke profile to database for user_id {user_id}")
                return True
                
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and retry_count < max_retries - 1:
                    retry_count += 1
                    print(f"⚠️ Database locked, retrying ({retry_count}/{max_retries})...")
                    import time
                    time.sleep(0.5)  # Wait 500ms before retry
                    continue
                else:
                    print(f"❌ Error saving keystroke profile: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                    
            except Exception as e:
                print(f"❌ Error saving keystroke profile: {e}")
                import traceback
                traceback.print_exc()
                return False
                
            finally:
                if conn:
                    conn.close()
        
        return False
    
    def get_user_keystroke_samples(self, username):
        """
        Retrieve the registered keystroke samples for a user from biometric_profile table
        Returns list of feature dictionaries with keys:
        [ks_count, ks_rate, dwell_mean, dwell_std, flight_mean, flight_std,
         digraph_mean, digraph_std, backspace_rate, wps, wpm]
        """
        conn = self._get_conn()
        try:
            # Get user_id from username
            user = self.find_user_by_name(username)
            if not user:
                print(f"❌ User '{username}' not found")
                return []
            
            user_id = user.get('user_id') or user.get('id')
            
            # Query biometric_profile table for this user's samples
            query = """
            SELECT typing_pattern 
            FROM biometric_profile 
            WHERE user_id = ? 
            ORDER BY created_date DESC
            """
            
            cursor = conn.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            if not rows:
                print(f"⚠️ No keystroke samples found for user_id {user_id}")
                return []
            
            print(f"📊 Retrieved {len(rows)} samples from database for user '{username}'")
            
            # Parse typing_pattern (stored as JSON string)
            samples = []
            for i, row in enumerate(rows):
                typing_pattern = row[0]
                
                # Parse JSON if stored as string
                if isinstance(typing_pattern, str):
                    try:
                        pattern_data = json.loads(typing_pattern)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Failed to parse JSON for sample {i+1}: {e}")
                        continue
                else:
                    pattern_data = typing_pattern
                
                samples.append(pattern_data)
                print(f"   Sample {i+1}: {list(pattern_data.keys())[:5]}... (showing first 5 keys)")
            
            return samples
            
        except Exception as e:
            print(f"❌ Error retrieving keystroke samples: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            conn.close()
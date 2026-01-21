"""
Initialize database with your schema
"""
import sqlite3
import os

# Get paths - FIXED
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend
DB_PATH = os.path.join(BASE_DIR, 'instance', 'biometric_app.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'typing_biometric.sql')  # Look in backend folder

def init_database():
    """Create database and tables from schema.sql"""
    
    # Create instance directory if it doesn't exist
    instance_dir = os.path.join(BASE_DIR, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"✅ Created instance directory: {instance_dir}")
    else:
        print(f"📁 Instance directory exists: {instance_dir}")
    
    # Debug: Show what we're looking for
    print(f"\n🔍 Looking for schema at: {SCHEMA_PATH}")
    print(f"📁 Schema exists: {os.path.exists(SCHEMA_PATH)}")
    
    # Check if schema.sql exists
    if not os.path.exists(SCHEMA_PATH):
        print(f"\n❌ Schema file not found!")
        print(f"Expected location: {SCHEMA_PATH}")
        print(f"\n💡 Please create 'typing_biometric.sql' in the backend folder")
        print(f"Backend folder: {BASE_DIR}")
        
        # List files in backend folder
        print(f"\n📂 Files in backend folder:")
        for file in os.listdir(BASE_DIR):
            if file.endswith('.sql'):
                print(f"   ✓ {file}")
        return
    
    print(f"✅ Schema file found!")
    print(f"📁 Database will be created at: {DB_PATH}")
    
    # Connect to database (creates it if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🗄️  Loading schema and creating tables...")
    
    # Read and execute schema
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
        
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print("\n✅ Database initialized successfully!")
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        # Show some table details
        print("\n📋 Key tables for our app:")
        for table_name in ['user', 'user_registration', 'biometric_profile']:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"\n   {table_name}:")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
    
    print("\n🎉 Database setup complete!")

if __name__ == '__main__':
    init_database()
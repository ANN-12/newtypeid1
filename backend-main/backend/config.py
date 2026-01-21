"""
Database initialization with SQLite WAL mode
Add this to your database setup file or run it once
"""
import sqlite3
import os

def enable_wal_mode():
    """Enable Write-Ahead Logging for better concurrency"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'instance', 'biometric_app.db')
    
    print(f"Enabling WAL mode for database: {db_path}")
    
    try:
        # Connect with increased timeout
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Enable WAL mode (Write-Ahead Logging)
        # This allows multiple readers and one writer simultaneously
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Increase cache size (in KB)
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        
        # Set busy timeout (milliseconds to wait for lock)
        cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds
        
        conn.commit()
        
        # Verify WAL mode is enabled
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        
        print(f"✅ Database journal mode: {mode}")
        print("✅ WAL mode enabled successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enabling WAL mode: {e}")
        return False

if __name__ == '__main__':
    enable_wal_mode()
-- User table
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- UserRegistration table
CREATE TABLE IF NOT EXISTS user_registration (
    registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_id INTEGER UNIQUE,
    user_id INTEGER NOT NULL,
    password TEXT NOT NULL,
    biometriclogin TEXT,
    registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- UserCredential table
CREATE TABLE IF NOT EXISTS user_credential (
    credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    registration_date TEXT,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- ← ADDED
    FOREIGN KEY (reg_id) REFERENCES user_registration(registration_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- BiometricProfile table
CREATE TABLE IF NOT EXISTS biometric_profile (
    biometric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reg_id INTEGER NOT NULL,
    sample_text TEXT,
    typing_pattern TEXT,
    created_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (reg_id) REFERENCES user_registration(registration_id)
);

-- LoginSession table
CREATE TABLE IF NOT EXISTS login_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reg_id INTEGER NOT NULL,
    login_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time TEXT,
    status TEXT,
    login_method TEXT,
    IP_address TEXT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (reg_id) REFERENCES user_registration(registration_id)
);

-- AuditLog table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    admin_id INTEGER,
    event_type TEXT,
    description TEXT,
    event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IP_address TEXT,
    status TEXT
);

-- AdminRegistration table
CREATE TABLE IF NOT EXISTS admin_registration (
    admin_reg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Admin table
-- Admin table (COMPLETE - with foreign key)
CREATE TABLE IF NOT EXISTS admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT,
    status TEXT,
    admin_reg_id INTEGER,  -- ← Links to AdminRegistration
    FOREIGN KEY (admin_reg_id) REFERENCES admin_registration(admin_reg_id)
);


-- AdminLogin table
CREATE TABLE IF NOT EXISTS admin_login (
    admin_session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    login_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time TEXT,
    IP_address TEXT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

-- MLModel table
CREATE TABLE IF NOT EXISTS ml_model (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    retrain_frequency TEXT,
    accuracy_metrics TEXT,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Dashboard (Admin) table
CREATE TABLE IF NOT EXISTS dashboard (
    dashboard_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    activity_log TEXT,
    last_login TEXT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

-- Report table
CREATE TABLE IF NOT EXISTS report (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    dashboard_id INTEGER,
    success_rate TEXT,
    failure_rate TEXT,
    remarks TEXT,
    generated_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id),
    FOREIGN KEY (dashboard_id) REFERENCES dashboard(dashboard_id)
);

-- Database meta table
CREATE TABLE IF NOT EXISTS database_meta (
    db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    db_name TEXT,
    storage_type TEXT,
    last_backup TEXT,
    access_control_list TEXT
);

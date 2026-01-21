import sqlite3
import json

conn = sqlite3.connect(
    r"c:\Users\User\Downloads\typing-biometric-auth-main\typing-biometric-auth-main\backend-main\backend\instance\biometric_app.db"
)


cursor = conn.cursor()

print("=" * 60)
print("📊 AFTER REGISTRATION - DATABASE CHECK")
print("=" * 60)

# ---------- USERS ----------
try:
    cursor.execute("SELECT user_id, name, email, created_at FROM user")
    users = cursor.fetchall()

    print(f"\n👥 USER TABLE ({len(users)} rows):")
    for u in users:
        print(f"   ID: {u[0]} | Name: {u[1]} | Email: {u[2]} | Created: {u[3]}")
except sqlite3.OperationalError:
    print("\n❌ user table not found")

# ---------- USER REGISTRATION ----------
try:
    cursor.execute("SELECT user_id, password FROM user_registration")
    regs = cursor.fetchall()

    print(f"\n🔐 USER_REGISTRATION TABLE ({len(regs)} rows):")
    for r in regs:
        print(f"   User {r[0]} | Password stored (hidden)")
except sqlite3.OperationalError:
    print("\n❌ user_registration table not found")

# ---------- BIOMETRIC PROFILE ----------
try:
    cursor.execute(
        "SELECT biometric_id, user_id, sample_text, typing_pattern FROM biometric_profile"
    )
    profiles = cursor.fetchall()

    print(f"\n🔬 BIOMETRIC_PROFILE TABLE ({len(profiles)} rows):")

    for i, p in enumerate(profiles, 1):
        print(f"\n   Profile {i}:")
        print(f"      Biometric ID: {p[0]}")
        print(f"      User ID: {p[1]}")
        print(f"      Sample Text: {p[2]}")

        if p[3]:
            pattern = json.loads(p[3])
            print(
                f"      Features: ks_count={pattern.get('ks_count')}, "
                f"wpm={pattern.get('wpm')}"
            )
        else:
            print("      Features: ❌ No typing data")
except sqlite3.OperationalError:
    print("\n❌ biometric_profile table not found")

print("\n" + "=" * 60)
print("✅ DATABASE CHECK COMPLETED")
print("=" * 60)

conn.close()

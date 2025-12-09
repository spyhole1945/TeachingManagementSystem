from sqlalchemy.orm import Session
from tms.infra.database import SessionLocal
from tms.infra.models import User
from tms.application.services.auth_service import AuthService

def reset_admin_password():
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"Resetting password for {admin.username}...")
            # Using AuthService hashing
            hashed = auth_service.hash_password("admin123")
            admin.hashed_password = hashed
            db.commit()
            print("Password reset to 'admin123' successful.")
        else:
            print("Admin user not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()

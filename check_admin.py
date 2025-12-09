from sqlalchemy.orm import Session
from tms.infra.database import SessionLocal
from tms.infra.models import User, UserRole

def check_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"Admin found: ID={admin.id}, Username={admin.username}, Role={admin.role}, IsActive={admin.is_active}")
            # print(f"Hashed Password: {admin.hashed_password}") 
        else:
            print("Admin user NOT found.")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()

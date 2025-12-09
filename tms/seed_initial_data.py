"""
Seed initial system data
"""
from sqlalchemy.orm import Session
from tms.infra.database import SessionLocal
from tms.application.services.auth_service import AuthService
from tms.infra.models import UserRole, User

def seed_admin(db: Session):
    """Create default admin user if not exists"""
    auth_service = AuthService(db)
    
    # Check if any admin exists
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin:
        print("  - Admin user already exists")
        return

    print("  - Creating default admin user (admin/admin123)...")
    auth_service.create_user(
        username="admin",
        email="admin@tms.com",
        password="admin123",
        full_name="System Administrator",
        role=UserRole.ADMIN
    )
    print("  - Admin user created")

def seed_initial_data():
    """Main seeder function"""
    db = SessionLocal()
    try:
        print("🌱 Seeding initial data...")
        seed_admin(db)
        print("✅ Seeding completed")
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
    finally:
        db.close()

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


def ensure_super_admin(db) -> User:
    admin = db.query(User).filter(User.role == "super_admin").first()
    if admin:
        admin.email = settings.super_admin_email
        admin.password_hash = hash_password(settings.super_admin_password)
        print("Updating Super Admin...")
    else:
        admin = User(
            email=settings.super_admin_email,
            password_hash=hash_password(settings.super_admin_password),
            role="super_admin",
        )
        db.add(admin)
        print("Creating Super Admin...")
    db.flush()
    print("Super Admin ready.")
    return admin

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


def ensure_super_admin(db) -> User | None:
    admin = db.query(User).filter(User.role == "super_admin").first()

    if admin:
        print("Super Admin ready.")
        return admin

    # No super admin exists — create it from env only. Never falls back to defaults.
    if not settings.super_admin_email or not settings.super_admin_password:
        print("No Super Admin: set SUPER_ADMIN_EMAIL/SUPER_ADMIN_PASSWORD to bootstrap.")
        return None

    print("Creating Super Admin...")
    admin = User(
        email=settings.super_admin_email,
        password_hash=hash_password(settings.super_admin_password),
        role="super_admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("Super Admin ready.")
    return admin

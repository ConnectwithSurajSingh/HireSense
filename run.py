import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from app import create_app, db
from app.models import User

port = int(os.environ.get("PORT", 5010))
app = create_app(port)


def seed_admin():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email="admin@hiresense.local").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@hiresense.local",
                role="admin",
                is_approved=True,
                is_active=True,
            )
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin@1234"))
            db.session.add(admin)
            db.session.commit()
        elif not admin.is_approved:
            admin.is_approved = True
            admin.is_active = True
            db.session.commit()


seed_admin()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false") == "true")

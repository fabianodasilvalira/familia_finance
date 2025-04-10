import logging
from sqlalchemy.orm import Session

from app.db.base import Base, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal, GoalContribution
from app.models.notification import Notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if we already have users
    user = db.query(User).first()
    if not user:
        logger.info("Creating initial admin user")
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            is_family_head=True,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        logger.info("Initial admin user created")

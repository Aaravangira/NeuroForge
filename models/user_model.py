"""
AI Invoice Extractor
User Authentication Model
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from database import Base


class User(Base):
    """
    User authenticated through Google OAuth.

    Each user receives 3 free invoice documents
    during the trial period.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    google_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=True,
    )

    picture = Column(
        String(1000),
        nullable=True,
    )

    plan = Column(
        String(50),
        nullable=False,
        default="trial",
    )

    trial_used = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"email={self.email!r}, "
            f"plan={self.plan!r}, "
            f"trial_used={self.trial_used}"
            f")>"
        )
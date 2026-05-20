from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    owner: Mapped[User] = relationship("User", back_populates="projects")
    decisions = relationship(
        "DecisionRecord",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    listeners = relationship(
        "Listener",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    alert_rules = relationship(
        "AlertRule",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    policy_config = relationship(
        "PolicyConfig",
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
    )
    decision_reports = relationship(
        "DecisionReport",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    api_keys = relationship(
        "ApiKey",
        back_populates="project",
        cascade="all, delete-orphan",
    )

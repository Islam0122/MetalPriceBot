from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)


class Supplier(Base):
    __tablename__ = 'suppliers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    site_url: Mapped[str] = mapped_column(String(100), nullable=True)

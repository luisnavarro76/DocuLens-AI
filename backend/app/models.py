"""
SQLAlchemy ORM models for users, documents, and chat messages.
"""
import uuid
import enum
import base64
import hashlib
from datetime import datetime, timezone

from cryptography.fernet import Fernet
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship

from app.database import Base


class EncryptedString(TypeDecorator):
    """
    A custom SQLAlchemy type that transparently encrypts strings in the database 
    using Fernet (AES). This ensures sensitive tokens aren't stored in plain text 
    while remaining easily accessible in code.
    """
    impl = Text
    cache_ok = False

    def _get_cipher(self):
        from app.config import get_settings
        settings = get_settings()
        # Derive a 32-byte key from the SECRET_KEY for Fernet encryption
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
        return Fernet(key)

    def process_bind_param(self, value, dialect):
        """Encrypt the value before saving to the database."""
        if value is None:
            return value
        cipher = self._get_cipher()
        return cipher.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        """Decrypt the value after reading from the database."""
        if value is None:
            return value
        cipher = self._get_cipher()
        try:
            return cipher.decrypt(value.encode()).decode()
        except Exception:
            # Fallback for unencrypted data or if decryption fails
            return value


def generate_uuid():
    """Generates a standard unique string identifier for database records."""
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    """
    Defines the available user roles for Role-Based Access Control (RBAC).
    - 'admin': Full access to system statistics and user management.
    - 'user': Standard access for uploading and chatting with documents.
    """
    user = "user"
    admin = "admin"


class User(Base):
    """
    Represents a registered user within the system.
    Supports both legacy 'is_admin' flags and the modern 'role' enum for permissions.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Permission fields: transitioning towards 'role', keeping 'is_admin' for compatibility
    role = Column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.user,
        nullable=False,
        server_default="user"
    )
    is_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True, index=True)
    hf_token = Column(EncryptedString, nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    """
    Stores secure hashes of API keys used for programmatic interaction with the system.
    """
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    key_prefix = Column(String(10), nullable=False)
    hashed_key = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Document(Base):
    """
    Metadata and processing status for files uploaded by users.
    """
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)         # Internal UUID-based filename
    original_name = Column(String(255), nullable=False)     # Original name for user display
    file_size = Column(Integer, default=0)                  # Size in bytes
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")          # pending | processing | ready | failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    summary = Column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")
    messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    Persistent log of conversations between users and the AI analyst.
    """
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True, index=True)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON representation of retrieved sources
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="messages")
    document = relationship("Document", back_populates="messages")
    shared_message = relationship("SharedMessage", back_populates="message", uselist=False, cascade="all, delete-orphan")


class SharedMessage(Base):
    """
    Links specific chat messages to public sharing URLs.
    """
    __tablename__ = "shared_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    message = relationship("ChatMessage", back_populates="shared_message")

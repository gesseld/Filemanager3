import uuid
from enum import Enum as PyEnum

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Index, Integer, LargeBinary, String, Text,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# Enums for auth system
class AuthProvider(str, PyEnum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"


class MFAMethod(str, PyEnum):
    TOTP = "totp"
    EMAIL = "email"
    SMS = "sms"


class TokenType(str, PyEnum):
    ACCESS = "access"
    REFRESH = "refresh"


# User Management Models
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_email", "email"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    mfa_enabled = Column(Boolean, default=False)
    mfa_method = Column(String(20))
    mfa_secret = Column(String(255))
    storage_quota = Column(Integer, default=1073741824)  # 1GB default
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    files = relationship("File", back_populates="user")
    permissions = relationship("Permission", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("idx_refresh_token_user", "user_id"),
        Index("idx_refresh_token_token", "token"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(512), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    device_info = Column(String(255))
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_account_id", name="unique_oauth_account"
        ),
        Index("idx_oauth_user", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(20), nullable=False)
    provider_account_id = Column(String(255), nullable=False)
    access_token = Column(String(512))
    refresh_token = Column(String(512))
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String(20))
    scope = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = (
        Index("idx_session_user", "user_id"),
        Index("idx_session_token", "session_token"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(512), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "resource_type", "resource_id", name="unique_permission"
        ),
        Index("idx_permission_user", "user_id"),
        Index("idx_permission_resource", "resource_type", "resource_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'file', 'folder', 'team'
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    can_read = Column(Boolean, default=False)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="permissions")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (Index("idx_role_name", "name"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        Index("idx_reset_token_user", "user_id"),
        Index("idx_reset_token_token", "token"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class File(Base):
    __tablename__ = "files"
    __table_args__ = (
        Index("idx_file_user", "user_id"),
        Index("idx_file_status", "status"),
        Index("idx_file_checksum", "checksum"),
        Index("idx_file_version", "version", "is_latest"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    path = Column(String(1024), nullable=False)
    size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)
    status = Column(String(50), default="active")
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    versions = relationship("FileVersion", back_populates="file")
    file_metadata = relationship("FileMetadata", back_populates="file")


class FileMetadata(Base):
    __tablename__ = "file_metadata"
    __table_args__ = (
        UniqueConstraint("file_id", "schema_id", name="unique_file_schema"),
        Index("idx_metadata_file", "file_id"),
        Index("idx_metadata_schema", "schema_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    schema_id = Column(
        UUID(as_uuid=True), ForeignKey("metadata_schemas.id"), nullable=False
    )
    values = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    file = relationship("File", back_populates="file_metadata")
    schema = relationship("MetadataSchema", back_populates="file_metadata_entries")


class MetadataSchema(Base):
    __tablename__ = "metadata_schemas"
    __table_args__ = (Index("idx_schema_name", "name"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    fields = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    file_metadata_entries = relationship("FileMetadata", back_populates="schema")


class SearchIndex(Base):
    __tablename__ = "search_indices"
    __table_args__ = (Index("idx_search_file", "file_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    file = relationship("File", back_populates="search_indices")


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = (Index("idx_embedding_file", "file_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    vector = Column(ARRAY(Float), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    file = relationship("File", back_populates="embeddings")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_file", "file_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    action = Column(String(50), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class LineageEvent(Base):
    __tablename__ = "lineage_events"
    __table_args__ = (Index("idx_lineage_file", "file_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    source = Column(String(255))
    destination = Column(String(255))
    operation = Column(String(100))
    parameters = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    file = relationship("File", back_populates="lineage_events")


# [All other model definitions remain unchanged...]

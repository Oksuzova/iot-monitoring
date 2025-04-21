"""Database configuration and initialization module for the IoT sensor application.

This module handles the PostgreSQL database connection configuration using SQLAlchemy.
It provides database session management and initialization functionality.

Environment Variables:
    DB_HOST: PostgreSQL server hostname (default: "postgres_db")
    DB_PORT: PostgreSQL server port (default: 5432)
    DB_NAME: Database name (default: "sensors")
    DB_USER: Database user (default: "user")
    DB_PASSWORD: Database password (default: "password")

Dependencies:
    - sqlalchemy: For database ORM and connection management
    - models: For database model definitions
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Database connection configuration with environment variable fallbacks
DB_HOST = os.getenv("DB_HOST", "postgres_db")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "sensors")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Construct PostgreSQL connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize the database by creating all defined tables.

    This function creates all tables that are defined in the SQLAlchemy models
    if they don't already exist in the database.

    Note:
        This should be called when the application starts, before any
        database operations are performed.
    """
    Base.metadata.create_all(bind=engine)
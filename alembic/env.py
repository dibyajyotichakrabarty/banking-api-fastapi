from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ye line important hai - models import karne ke liye
sys.path.append(os.getcwd())

from models import Base

# .env file load karo local testing ke liye
load_dotenv()

# this is the Alembic Config object
config = context.config

# ↓↓↓ YE PART SABSE IMPORTANT HAI ↓↓↓
# Render se DATABASE_URL environment variable lo
DATABASE_URL = os.getenv("DATABASE_URL")

# Render Postgres ka "postgres://" ko "postgresql://" me convert karo
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Alembic ko batao ki ye URL use karna hai
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
# ↑↑↑ YAHAN TAK ZARURI HAI ↑↑↑

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    

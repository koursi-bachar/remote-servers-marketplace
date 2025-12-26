import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.database import Base

from app.users.models import *
from app.machines.models import *
from app.listings.models import *
from app.bookings.models import *
from app.credentials.models import *
from app.compliance.models import *
from app.disputes.models import *
from app.organizations.models import *
from app.payments.models import *
from app.providers.models import *
from app.invoices.models import *
from app.benchmarks.models import *
from app.metrics.models import *


from dotenv import load_dotenv
load_dotenv()


# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import model metadata for 'autogenerate' support if needed
target_metadata = Base.metadata

# Read DATABASE_URL (or TEST_DATABASE_URL) from environment
db_url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL")

if not db_url:
    raise RuntimeError("No DATABASE_URL or TEST_DATABASE_URL set in environment.")

# Convert deprecated postgres:// to postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Set URL into Alembic config
config.set_main_option("sqlalchemy.url", db_url)


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
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
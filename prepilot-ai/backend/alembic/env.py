import os
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.sql import column, table

# Add project root to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import Base and models
from app.database import Base

# Set target metadata for autogenerate
target_metadata = Base.metadata

# Get DATABASE_URL from environment
def get_database_url():
    """Get DATABASE_URL from environment, overriding alembic.ini if needed."""
    return os.getenv("DATABASE_URL", "")

# Override sqlalchemy.url if DATABASE_URL is set
if get_database_url():
    os.environ["SQLALCHEMY_URL"] = get_database_url()

# other values from the config, defined by the config file.
script_location = context.config.ScriptDirectory
import os
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import text
from oc4ids_datastore_api.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Initializing database...")
    
    # Check if init.sql exists
    init_sql_path = "init.sql"
    if not os.path.exists(init_sql_path):
        logger.error("init.sql not found!")
        return

    # Read SQL file
    with open(init_sql_path, "r") as f:
        sql_script = f.read()

    with engine.connect() as conn:
        # Drop all tables first (Force clean slate)
        # Note: CASCADE is dangerous in prod, but fine for dev
        logger.info("Dropping existing tables...")
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()

        # Run init.sql
        logger.info("Running init.sql script...")
        # Split by ';' to run statement by statement if needed, 
        # but usually SQLAlchemy text() can handle blocks if syntax is standard.
        # However, for big scripts, it's safer to execute as one block or split if supported.
        conn.execute(text(sql_script))
        conn.commit()
    
    logger.info("Database initialized successfully from init.sql!")

if __name__ == "__main__":
    init_db()

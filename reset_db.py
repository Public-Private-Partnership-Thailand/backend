from dotenv import load_dotenv
load_dotenv()

from sqlmodel import SQLModel, text, Session
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import * # Import all models to ensure metadata is populated

def reset_db():
    print("Resetting database...")
    with Session(engine) as session:
        # Drop public schema cascade to wipe everything clearly
        session.exec(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"))
        session.commit()
    
    print("Creating new tables...")
    SQLModel.metadata.create_all(engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()

from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, select
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import AdditionalClassification

def create_test_data():
    print("Starting creation of test Additional Classifications...")
    
    test_data = [
        {
            "scheme": "รูปแบบการจัดสรรกรรมสิทธิ์",
            "code": "test_contract",
            "description": "test_contract"
        },
        {
            "scheme": "รูปแบบสัมปทานหรือค่าตอบแทน",
            "code": "test_concession",
            "description": "test_concession"
        }
    ]

    with Session(engine) as session:
        for item in test_data:
            # Check if exists
            statement = select(AdditionalClassification).where(
                AdditionalClassification.scheme == item["scheme"],
                AdditionalClassification.code == item["code"]
            )
            existing = session.exec(statement).first()
            
            if existing:
                print(f"Skipping existing: {item['code']} ({item['scheme']})")
            else:
                new_obj = AdditionalClassification(
                    scheme=item["scheme"],
                    code=item["code"],
                    description=item["description"]
                )
                session.add(new_obj)
                print(f"Created: {item['code']} ({item['scheme']})")
        
        session.commit()
        print("Data creation complete.")

if __name__ == "__main__":
    create_test_data()

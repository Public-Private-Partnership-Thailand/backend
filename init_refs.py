from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, select
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import Sector, Ministry, ProjectType, AdditionalClassification

DATA = {
    "sector": [
        {"id": 1, "value": "transport.road"},
        {"id": 2, "value": "transport.rail"},
        {"id": 3, "value": "transport.air"},
        {"id": 4, "value": "transport.water"},
        {"id": 5, "value": "waterAndWaste"},
        {"id": 6, "value": "energy"},
        {"id": 7, "value": "communications"},
        {"id": 8, "value": "health"},
        {"id": 9, "value": "education"},
        {"id": 10, "value": "socialHousing"},
        {"id": 11, "value": "cultureSportsAndRecreation"},
        {"id": 12, "value": "others"}
    ],
    "ministry": [
        {"id": 1, "value": "กระทรวงกลาโหม"},
        {"id": 2, "value": "กระทรวงการคลัง"},
        {"id": 3, "value": "กระทรวงการต่างประเทศ"},
        {"id": 4, "value": "กระทรวงการท่องเที่ยวและกีฬา"},
        {"id": 5, "value": "กระทรวงการพัฒนาสังคมและความมั่นคงของมนุษย์"},
        {"id": 6, "value": "กระทรวงการอุดมศึกษา วิทยาศาสตร์ วิจัยและนวัตกรรม"},
        {"id": 7, "value": "กระทรวงเกษตรและสหกรณ์"},
        {"id": 8, "value": "กระทรวงคมนาคม"},
        {"id": 9, "value": "กระทรวงทรัพยากรธรรมชาติและสิ่งแวดล้อม"},
        {"id": 10, "value": "กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม"},
        {"id": 11, "value": "กระทรวงพลังงาน"},
        {"id": 12, "value": "กระทรวงพาณิชย์"},
        {"id": 13, "value": "กระทรวงมหาดไทย"},
        {"id": 14, "value": "กระทรวงยุติธรรม"},
        {"id": 15, "value": "กระทรวงแรงงาน"},
        {"id": 16, "value": "กระทรวงวัฒนธรรม"},
        {"id": 17, "value": "กระทรวงศึกษาธิการ"},
        {"id": 18, "value": "กระทรวงสาธารณสุข"},
        {"id": 19, "value": "กระทรวงอุตสาหกรรม"},
        {"id": 20, "value": "สำนักนายกรัฐมนตรี"},
        {"id": 21, "value": "อื่น ๆ"}
    ],
    "contractType": [
        {"id": 1, "value": "BTO"},
        {"id": 2, "value": "BOT"},
        {"id": 3, "value": "BTO/BOT"}
    ],
    "projectType": [
        {"id": 1, "value": "ท่าเรือ"},
        {"id": 2, "value": "รถไฟฟ้า"},
        {"id": 3, "value": "ท่าอากาศยาน"},
        {"id": 4, "value": "ทางพิเศษ"},
        {"id": 5, "value": "รถไฟ"},
        {"id": 6, "value": "ทางหลวง"},
        {"id": 7, "value": "ศูนย์นิทรรศการและศูนย์การประชุม"},
        {"id": 8, "value": "การขนส่งทางถนน"}
    ],
    "concessionForm": [
        {"id": 1, "value": "PPP Net Cost"},
        {"id": 2, "value": "Gross Cost"},
        {"id": 3, "value": "อื่น ๆ"}
    ]
}

def init_sectors(session):
    print("Initializing Sectors...")
    for item in DATA["sector"]:
        code = item["value"]
        # Assuming category is same as code for now if not provided
        category = code 
        
        obj = session.exec(select(Sector).where(Sector.code == code)).first()
        if not obj:
            obj = Sector(
                code=code, 
                name_th=code, # Fallback
                name_en=code, 
                category=category,
                description=code
            )
            session.add(obj)
            print(f"Created Sector: {code}")
        else:
            print(f"Sector exists: {code}")

def init_ministries(session):
    print("Initializing Ministries...")
    for item in DATA["ministry"]:
        name = item["value"]
        obj = session.exec(select(Ministry).where(Ministry.name_th == name)).first()
        if not obj:
            obj = Ministry(name_th=name, name_en=name) # name_en fallback
            session.add(obj)
            print(f"Created Ministry: {name}")
        else:
            print(f"Ministry exists: {name}")

def init_contract_types(session):
    print("Initializing Contract Types (Ownership)...")
    scheme = "รูปแบบการจัดสรรกรรมสิทธิ์"
    for item in DATA["contractType"]:
        val = item["value"]
        obj = session.exec(select(AdditionalClassification).where(
            AdditionalClassification.scheme == scheme,
            AdditionalClassification.code == val
        )).first()
        if not obj:
            # Using value as code and description
            obj = AdditionalClassification(scheme=scheme, code=val, description=val)
            session.add(obj)
            print(f"Created Contract Type: {val}")
        else:
            print(f"Contract Type exists: {val}")

def init_project_types(session):
    print("Initializing Project Types...")
    for item in DATA["projectType"]:
        name = item["value"]
        pt_id = item["id"]
        code = f"PT{pt_id:02d}"
        
        obj = session.exec(select(ProjectType).where(ProjectType.name_th == name)).first()
        if not obj:
            obj = ProjectType(
                code=code, 
                name_th=name, 
                name_en=f"Project Type {pt_id}", # Placeholder English name
                description=name
            )
            session.add(obj)
            print(f"Created Project Type: {name}")
        else:
            print(f"Project Type exists: {name}")

def init_concession_forms(session):
    print("Initializing Concession Forms...")
    scheme = "รูปแบบสัมปทานหรือค่าตอบแทน"
    for item in DATA["concessionForm"]:
        val = item["value"]
        
        # Check by code (value) OR description (value) just in case
        obj = session.exec(select(AdditionalClassification).where(
            AdditionalClassification.scheme == scheme,
            AdditionalClassification.code == val
        )).first()
        
        if not obj:
            obj = AdditionalClassification(scheme=scheme, code=val, description=val)
            session.add(obj)
            print(f"Created Concession Form: {val}")
        else:
            print(f"Concession Form exists: {val}")

from sqlalchemy import text # Import text

# ... (data definitions remain same)

def sync_sequences(session):
    print("Syncing sequences...")
    tables = [
        "additional_classifications", 
        "sector", 
        "ministry", 
        "project_type"
    ]
    for table in tables:
        try:
            # Reset sequence to max(id)
            sql = text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(max(id), 0) + 1, false) FROM {table};")
            session.exec(sql)
            print(f"Synced sequence for {table}")
        except Exception as e:
            print(f"Note: Could not sync sequence for {table}: {e}")

def main():
    with Session(engine) as session:
        try:
            sync_sequences(session) # Sync first
            init_sectors(session)
            init_ministries(session)
            init_contract_types(session)
            init_project_types(session)
            init_concession_forms(session)
            session.commit()
            print("All reference data initialized successfully.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
            raise e

if __name__ == "__main__":
    main()

from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, select
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import Sector, Ministry, ProjectType, AdditionalClassification

DATA = {
    "sector": [
        {"id": 0, "value": "transport"},        # Parent sector
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
    "cofog": [
        {"code": "04.5",   "description": "Transport"},
        {"code": "04.5.1", "description": "Road transport (CS)"},
        {"code": "04.5.2", "description": "Water transport (CS)"},
        {"code": "04.5.3", "description": "Railway transport (CS)"},
        {"code": "04.5.4", "description": "Air transport (CS)"},
        {"code": "04.5.5", "description": "Pipeline and other transport (CS)"},
        {"code": "04.6",   "description": "Communication"},
        {"code": "06.0",   "description": "Housing and community amenities"},
        {"code": "07.0",   "description": "Health"},
        {"code": "09.0",   "description": "Education"},
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

def init_cofog(session):
    print("Initializing COFOG Classifications...")
    scheme = "COFOG"
    for item in DATA["cofog"]:
        code = item["code"]
        desc = item["description"]
        obj = session.exec(select(AdditionalClassification).where(
            AdditionalClassification.scheme == scheme,
            AdditionalClassification.code == code
        )).first()
        if not obj:
            obj = AdditionalClassification(scheme=scheme, code=code, description=desc)
            session.add(obj)
            print(f"Created COFOG: {code} - {desc}")
        else:
            print(f"COFOG exists: {code}")

from sqlalchemy import text


# ===================================
# RISK SEED DATA
# ===================================

RISK_CATEGORIES = [
    ("LAND_SITE", "Land availability, access & site",
     "The risk associated with selecting land suitable for the project; providing it with good title and free of encumbrances; addressing indigenous rights; obtaining necessary planning approvals; providing access to the site; site security; and site and existing asset condition.",
     "ความเสี่ยงที่เกี่ยวกับการได้มาซึ่งที่ดินที่เหมาะสม กรรมสิทธิ์ที่ดินที่ปราศจากภาระผูกพัน"),
    ("SOCIAL", "Social",
     "The risk associated with the project impact on adjacent properties and affected people (including public protest and unrest); resettlement; indigenous land rights; and industrial action.",
     "ความเสี่ยงจากผลกระทบของโครงการต่อทรัพย์สินข้างเคียงและประชาชนที่ได้รับผลกระทบ"),
    ("ENVIRONMENTAL", "Environmental",
     "The risk associated with pre-existing conditions; obtaining consents; compliance with laws; conditions caused by the project; external events; and climate change.",
     "ความเสี่ยงด้านสิ่งแวดล้อม"),
    ("DESIGN", "Design",
     "The risk that the project design is not suitable for the purpose required; approval of design; and changes.",
     "ความเสี่ยงที่การออกแบบโครงการไม่เหมาะสมกับวัตถุประสงค์ที่ต้องการ"),
    ("CONSTRUCTION", "Construction",
     "The risk of construction costs exceeding modelled costs; completion delays; project management; interface; quality standards compliance; health and safety; defects; intellectual property rights compliance; industrial action; and vandalism.",
     "ความเสี่ยงด้านต้นทุนก่อสร้างที่เกินงบประมาณ"),
    ("VARIATIONS", "Variations",
     "The risk of changes requested by either party to the service which affect construction or operation.",
     "ความเสี่ยงจากการเปลี่ยนแปลงบริการที่ร้องขอโดยฝ่ายใดฝ่ายหนึ่ง"),
    ("OPERATING", "Operating Risk",
     "The risk of events affecting performance or increasing costs beyond modelled costs; performance standards and price; availability of resources; intellectual property rights compliance; health and safety; compliance with maintenance standards; industrial action; and vandalism.",
     "ความเสี่ยงจากเหตุการณ์ที่กระทบต่อประสิทธิภาพหรือเพิ่มต้นทุนดำเนินงาน"),
    ("DEMAND", "Demand",
     "The risk of traffic levels being different to forecast levels; the consequences for revenue and costs; and government support measures.",
     "ความเสี่ยงจากปริมาณการใช้บริการที่แตกต่างจากที่พยากรณ์ไว้"),
    ("FIN_MARKET", "Financial markets",
     "The risk of inflation; exchange rate fluctuation; interest rate fluctuation; unavailability of insurance; and refinancing.",
     "ความเสี่ยงด้านตลาดการเงิน"),
    ("STRATEGIC", "Strategic/partnering risk",
     "The risk of the Private Partner and/or its sub-contractors not being the right choice to deliver the project; Contracting Authority intervention in the project; ownership changes; and disputes.",
     "ความเสี่ยงจากการเลือกพันธมิตรภาคเอกชนและผู้รับเหมาที่ไม่เหมาะสม"),
    ("DISRUPT_TECH", "Disruptive technology",
     "The risk that a new emerging technology unexpectedly displaces an established technology or the risk of obsolescence of equipment or materials used.",
     "ความเสี่ยงจากเทคโนโลยีใหม่ที่เข้ามาแทนที่เทคโนโลยีที่ใช้อยู่โดยไม่คาดคิด"),
    ("FORCE_MAJEURE", "Force majeure",
     "The risk that unexpected events occur that are beyond the control of the parties and delay or prevent performance.",
     "ความเสี่ยงจากเหตุการณ์ที่ไม่คาดคิดและอยู่นอกเหนือการควบคุมของคู่สัญญา"),
    ("POLITICAL", "Political",
     "Risks arising from government actions, policy changes, regulatory instability, or political interference that may affect project approvals, contractual conditions, or overall project continuity.",
     "ความเสี่ยงจากการดำเนินการของรัฐบาล การเปลี่ยนแปลงนโยบาย"),
    ("LAW", "Law",
     "The risk of compliance with applicable law; and changes in law affecting performance of the project or the Private Partner's costs.",
     "ความเสี่ยงจากการไม่ปฏิบัติตามกฎหมายที่บังคับใช้"),
    ("EARLY_TERMINATION", "Early termination",
     "The risk of a project being terminated before its natural expiry on various grounds.",
     "ความเสี่ยงจากการยกเลิกโครงการก่อนกำหนด"),
    ("HANDBACK_COND", "Condition at handback",
     "The risk of deterioration of the project assets/land during the life of the PPP.",
     "ความเสี่ยงจากการเสื่อมสภาพของสินทรัพย์หรือที่ดินโครงการตลอดอายุ PPP"),
    ("PROJECT_SELECTION", "Project selected",
     "Project selection risks.",
     "ความเสี่ยงในกระบวนการคัดเลือกโครงการ PPP"),
    ("RELATIONSHIP", "Relationship",
     "Risks from quality of collaboration between public and private partners.",
     "ความเสี่ยงด้านคุณภาพของความร่วมมือระหว่างภาครัฐและเอกชน"),
    ("PROJECT_FINANCE", "Project finance",
     "Risks related to financial structure and attractiveness of a PPP project to investors.",
     "ความเสี่ยงด้านโครงสร้างทางการเงินและความน่าดึงดูดของโครงการ PPP"),
    ("PROCUREMENT", "Procurement Risks",
     "Risks related to the tendering and contracting process, including non-transparent selection procedures, uncompetitive bidding, poor negotiation, or delays in award decisions.",
     "ความเสี่ยงในกระบวนการประมูลและการทำสัญญา"),
]

CATEGORY_FACTOR_LINKS = [
    (1, 104), (1, 127), (1, 103), (1, 105), (1, 50), (1, 112), (1, 123), (1, 71), (1, 121), (1, 1), (1, 116), (1, 135), (1, 115), (1, 37), (1, 102),
    (2, 12), (2, 112), (2, 51), (2, 64),
    (3, 96), (3, 86), (3, 15), (3, 35), (3, 38), (3, 11), (3, 140),
    (4, 122), (4, 2), (4, 10), (4, 8),
    (5, 25), (5, 141), (5, 100), (5, 108), (5, 49), (5, 77), (5, 27), (5, 68), (5, 64), (5, 136), (5, 110), (5, 4), (5, 139), (5, 133), (5, 22), (5, 66), (5, 95), (5, 20),
    (6, 137),
    (7, 63), (7, 89), (7, 87), (7, 68), (7, 49), (7, 77), (7, 82), (7, 70), (7, 64), (7, 136), (7, 109), (7, 54), (7, 46), (7, 113), (7, 17), (7, 79), (7, 114), (7, 29), (7, 101),
    (8, 47), (8, 19), (8, 55), (8, 80), (8, 48),
    (9, 65), (9, 36), (9, 69), (9, 128), (9, 111), (9, 67), (9, 125), (9, 84), (9, 83), (9, 41), (9, 42),
    (10, 98), (10, 119), (10, 7), (10, 90), (10, 5), (10, 129), (10, 99), (10, 57), (10, 106), (10, 33),
    (11, 34),
    (12, 45), (12, 44),
    (13, 92), (13, 134), (13, 94), (13, 24), (13, 91), (13, 28),
    (14, 14), (14, 6), (14, 9), (14, 61), (14, 18),
    (15, 23), (15, 21), (15, 81), (15, 138), (15, 43), (15, 97), (15, 118),
    (16, 16), (16, 3),
    (17, 107), (17, 76), (17, 93), (17, 60),
    (18, 32), (18, 59), (18, 72), (18, 88), (18, 126), (18, 58), (18, 62), (18, 117), (18, 26), (18, 85),
    (19, 39), (19, 53), (19, 73), (19, 52), (19, 30), (19, 56), (19, 74), (19, 31), (19, 40),
    (20, 131), (20, 13), (20, 75), (20, 120), (20, 124), (20, 130), (20, 132), (20, 78),
]

RISK_PHASES = [
    (1, 1, "pre-construction", "identification to preparation phases"),
    (2, 2, "construction", "implementation and completion phases"),
    (3, 4, "operation", "maintenance and decommissioning phases")
]

def init_risk_phases():
    print("Initializing Risk Phases...")
    inserted = updated = 0
    with engine.begin() as conn:
        for phase_id, phase_id_from_bit_mask, phase_name, meaning in RISK_PHASES:
            row = conn.execute(
                text("""
                    INSERT INTO risk_phase (phase_id, phase_id_from_bit_mask, phase_name, meaning)
                    VALUES (:phase_id, :phase_id_from_bit_mask, :phase_name, :meaning)
                    ON CONFLICT (phase_id) DO UPDATE
                        SET phase_id_from_bit_mask = EXCLUDED.phase_id_from_bit_mask,
                            phase_name = EXCLUDED.phase_name,
                            meaning = EXCLUDED.meaning
                    RETURNING phase_id, (xmax = 0) AS ins
                """),
                {"phase_id": phase_id, "phase_id_from_bit_mask": phase_id_from_bit_mask, "phase_name": phase_name, "meaning": meaning},
            ).fetchone()
            if row[1]:
                inserted += 1
            else:
                updated += 1
    print(f"  Risk Phases done — Inserted: {inserted}, Updated: {updated}")


def init_risk_categories():
    print("Initializing Risk Categories...")
    inserted = updated = 0
    with engine.begin() as conn:
        for code, name, desc_en, desc_th in RISK_CATEGORIES:
            row = conn.execute(
                text("""
                    INSERT INTO risk_category (category_code, category_name, description_en, description_th)
                    VALUES (:code, :name, :desc_en, :desc_th)
                    ON CONFLICT (category_code) DO UPDATE
                        SET category_name  = EXCLUDED.category_name,
                            description_en = EXCLUDED.description_en,
                            description_th = EXCLUDED.description_th
                    RETURNING category_code, (xmax = 0) AS ins
                """),
                {"code": code, "name": name, "desc_en": desc_en, "desc_th": desc_th},
            ).fetchone()
            if row[1]:
                inserted += 1
            else:
                updated += 1
    print(f"  Risk Categories done — Inserted: {inserted}, Updated: {updated}")


def init_risk_factors():
    """Delegates to the existing seed_risk_factors script."""
    print("Initializing Risk Factors...")
    import importlib.util, os
    script = os.path.join(os.path.dirname(__file__), "scripts", "seed_risk_factors.py")
    spec = importlib.util.spec_from_file_location("seed_risk_factors", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def init_category_factor_links():
    print("Initializing Category-Factor Links...")
    inserted = 0
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM category_factor_link"))
        for cat_id, fac_id in CATEGORY_FACTOR_LINKS:
            try:
                conn.execute(
                    text("""
                        INSERT INTO category_factor_link (risk_category_id, risk_factor_id)
                        VALUES (:cat_id, :fac_id)
                        ON CONFLICT DO NOTHING
                    """),
                    {"cat_id": cat_id, "fac_id": fac_id},
                )
                inserted += 1
            except Exception as e:
                print(f"  Warning: {cat_id} -> {fac_id}: {e}")
    print(f"  Category-Factor Links inserted: {inserted}")


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
            sql = text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(max(id), 0) + 1, false) FROM {table};")
            session.exec(sql)
            print(f"Synced sequence for {table}")
        except Exception as e:
            print(f"Note: Could not sync sequence for {table}: {e}")


def main():
    with Session(engine) as session:
        try:
            sync_sequences(session)
            init_sectors(session)
            init_ministries(session)
            init_contract_types(session)
            init_project_types(session)
            init_concession_forms(session)
            init_cofog(session)
            session.commit()
            print("All reference data initialized successfully.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
            raise e

    # Risk seeds (idempotent upsert, run after session commit)
    try:
        init_risk_categories()
        init_risk_factors()
        init_category_factor_links()
        init_risk_phases()
        print("All risk seed data initialized successfully.")
    except Exception as e:
        print(f"An error occurred during risk seeding: {e}")
        raise e

    # Import risk patterns (from CSV)
    try:
        import importlib.util, os
        script = os.path.join(os.path.dirname(__file__), "scripts", "import_risk_pattern.py")
        spec = importlib.util.spec_from_file_location("import_risk_pattern", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("Importing Risk Patterns...")
        mod.import_risk_patterns()
        print("Risk patterns imported successfully.")
    except Exception as e:
        print(f"An error occurred during risk pattern import: {e}")
        raise e

    # Import project data
    #try:
    #    script = os.path.join(os.path.dirname(__file__), "scripts", "import_data.py")
    #    spec = importlib.util.spec_from_file_location("import_data", script)
    #    mod = importlib.util.module_from_spec(spec)
    #    spec.loader.exec_module(mod)
    #    print("Importing project data...")
    #    mod.import_data_direct()
    #    print("Project data imported successfully.")
    #except Exception as e:
    #    print(f"An error occurred during project data import: {e}")
    #    raise e


if __name__ == "__main__":
    main()

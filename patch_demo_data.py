import os
from sqlmodel import create_engine, Session, select
from oc4ids_datastore_api.models import Project, AdditionalClassification

def patch_demo_data():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Error: DATABASE_URL not set")
        return

    engine = create_engine(url)

    with Session(engine) as session:
        # 1. Find the project (M75)
        # Using a partial match on title if ID not known, but ID e73caee6... was seen before
        # Let's search by title pattern
        stmt = select(Project).where(Project.title.ilike("%M75%"))
        project = session.exec(stmt).first()
        
        if not project:
            print("Demo project not found!")
            return

        print(f"Found project: {project.title} (ID: {project.id})")

        # 2. Prepare Classifications to Add (Standard Thai Schemes)
        classifications_to_add = [
            {
                "scheme": "รูปแบบการจัดสรรกรรมสิทธิ์", # Contract Type
                "id": "PPP Net Cost",
                "description": "PPP Net Cost"
            },
            {
                "scheme": "รูปแบบสัมปทานหรือค่าตอบแทน", # Concession Form
                "id": "BTO",
                "description": "Build-Transfer-Operate (BTO)"
            },
            {
                "scheme": "ขอบเขตการลงทุน", # Investment Scope
                "id": "DBFOM",
                "description": "Design, Build, Finance, Operate, Maintain"
            }
        ]

        # 3. Add/Link Classifications
        # Note: We need to handle ProjectAdditionalClassificationLink manually if many-to-many isn't auto-managed by simple append
        # But SQLModel relationship should handle it if defined correctly.
        # Let's check if they exist first.

        for c_data in classifications_to_add:
            stmt = select(AdditionalClassification).where(
                AdditionalClassification.scheme == c_data["scheme"],
                AdditionalClassification.code == c_data["id"]
            )
            ac_obj = session.exec(stmt).first()
            
            if not ac_obj:
                print(f"Creating new classification: {c_data['scheme']} - {c_data['description']}")
                ac_obj = AdditionalClassification(
                    scheme=c_data["scheme"],
                    code=c_data["id"],
                    description=c_data["description"]
                )
                session.add(ac_obj)
                session.flush() # Get ID
            
            # Check if linked
            if ac_obj not in project.additional_classifications:
                print(f"Linking {c_data['description']} to project...")
                project.additional_classifications.append(ac_obj)
            else:
                 print(f"Already linked: {c_data['description']}")

        session.add(project)
        session.commit()
        print("Patch completed successfully.")

if __name__ == "__main__":
    patch_demo_data()

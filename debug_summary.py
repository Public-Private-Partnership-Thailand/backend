import os
import sys
from sqlmodel import create_engine, Session
from oc4ids_datastore_api.services import get_dashboard_summary
from oc4ids_datastore_api.daos import ProjectDAO

# Setup DB
url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL mismatch")
    sys.exit(1)

engine = create_engine(url)

with Session(engine) as session:
    print("Calling get_dashboard_summary...")
    try:
        # Test with no filters
        res = get_dashboard_summary(session)
        print("Success (No filter)")
        
        # Test with Contract Type filter (ID 1 - Road transport)
        res = get_dashboard_summary(session, contract_type_id=[1])
        print(f"Success (Contract Type 1) - Found: {res['summary']['totalProjects']}")

        # Test with PPP Net Cost (ID 2)
        res = get_dashboard_summary(session, contract_type_id=[2])
        print(f"Success (Contract Type 2 - PPP Net Cost) - Found: {res['summary']['totalProjects']}")

        # Test with Sector 1 (Transport)
        res = get_dashboard_summary(session, sector_id=[1])
        print(f"Success (Sector 1 - Transport) - Found: {res['summary']['totalProjects']}")
        
        # Test with Sector 2 (Road)
        res = get_dashboard_summary(session, sector_id=[2])
        print(f"Success (Sector 2 - Road) - Found: {res['summary']['totalProjects']}")

        # Test Combined (Sector 1 + Contract 2)
        res = get_dashboard_summary(session, sector_id=[1], contract_type_id=[2])
        print(f"Success (Sector 1 + Contract 2) - Found: {res['summary']['totalProjects']}")

        # Test Ministry 1 (Motorways UK)
        res = get_dashboard_summary(session, ministry_id=[1])
        print(f"Success (Ministry 1) - Found: {res['summary']['totalProjects']}")
        
        # Test Combined All (Sector 1 + Contract 1 + Ministry 1)
        res = get_dashboard_summary(session, sector_id=[1], contract_type_id=[1], ministry_id=[1])
        print(f"Success (All 3) - Found: {res['summary']['totalProjects']}")


        
    except Exception as e:
        import traceback
        traceback.print_exc()

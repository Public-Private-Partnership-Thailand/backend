"""
Seed script: bulk insert risk categories into the `risk_category` table.
Skips any category whose category_code already exists (idempotent).

Usage (from /home/ben/CU_PPP/backend):
    python scripts/seed_risk_categories.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment / .env")

# (code, name, description) — description is ignored here since the table has no such column
RISK_CATEGORIES = [
    ("LAND_SITE",         "Land availability, access & site", "The risk associated with selecting land suitable for the project; providing it with good title and free of encumbrances; addressing indigenous rights; obtaining necessary planning approvals; providing access to the site; site security; and site and existing asset condition."),
    ("SOCIAL",            "Social",                           "The risk associated with the project impact on adjacent properties and affected people (including public protest and unrest); resettlement; indigenous land rights; and industrial action."),
    ("ENVIRONMENTAL",     "Environmental",                    "The risk associated with pre-existing conditions; obtaining consents; compliance with laws; conditions caused by the project; external events; and climate change."),
    ("DESIGN",            "Design",                           "The risk that the project design is not suitable for the purpose required; approval of design; and changes."),
    ("CONSTRUCTION",      "Construction",                     "The risk of construction costs exceeding modelled costs; completion delays; project management; interface; quality standards compliance; health and safety; defects; intellectual property rights compliance; industrial action; and vandalism."),
    ("VARIATIONS",        "Variations",                       "The risk of changes requested by either party to the service which affect construction or operation."),
    ("OPERATING",         "Operating",                        "The risk of events affecting performance or increasing costs beyond modelled costs; performance standards and price; availability of resources; intellectual property rights compliance; health and safety; compliance with maintenance standards; industrial action; and vandalism."),
    ("DEMAND",            "Demand",                           "The risk of traffic levels being different to forecast levels; the consequences for revenue and costs; and government support measures."),
    ("FIN_MARKET",        "Financial markets",                "The risk of inflation; exchange rate fluctuation; interest rate fluctuation; unavailability of insurance; and refinancing."),
    ("STRATEGIC",         "Strategic / Partnering",           "The risk of the Private Partner and/or its sub-contractors not being the right choice to deliver the project; Contracting Authority intervention in the project; ownership changes; and disputes."),
    ("DISRUPT_TECH",      "Disruptive technology",            "The risk that a new emerging technology unexpectedly displaces an established technology or the risk of obsolescence of equipment or materials used."),
    ("FORCE_MAJEURE",     "Force majeure",                    "The risk that unexpected events occur that are beyond the control of the parties and delay or prevent performance."),
    ("POLITICAL",         "Political",                        "Risks arising from government actions, policy changes, regulatory instability, or political interference that may affect project approvals, contractual conditions, or overall project continuity."),
    ("LAW",               "Law",                              "The risk of compliance with applicable law; and changes in law affecting performance of the project or the Private Partner's costs."),
    ("EARLY_TERMINATION", "Early termination",                "The risk of a project being terminated before its natural expiry on various grounds; the financial consequences of such termination; and the strength of the Contracting Authority's payment covenant."),
    ("HANDBACK_COND",     "Condition at handback",            "The risk of deterioration of the project assets/land during the life of the PPP and the risk that the project assets/land are not in the contractually required condition at the time of handback to the Contracting Authority."),
    ("PROJECT_SELECTION", "Project selected",                 "Project selection refers to the process of choosing PPP projects that are socially acceptable, technically feasible, and aligned with public demand, where risks may arise from public opposition, inappropriate tendering, or poor assessment of project suitability."),
    ("RELATIONSHIP",      "Relationship",                     "Relationship refers to the quality of collaboration, coordination, and mutual understanding between public and private partners in PPP projects, where differences in working methods, responsibilities, and communication can create significant risks."),
    ("PROJECT_FINANCE",   "Project finance",                  "Project finance refers to the financial structure and attractiveness of a PPP project to investors, including the availability of financing, cost of capital, and the project's ability to generate sufficient returns to support long-term investment."),
    ("PROCUREMENT",       "Procurement risks",                "Risks related to the tendering and contracting process, including non-transparent selection procedures, uncompetitive bidding, poor negotiation, or delays in award decisions that may impact project performance and fairness."),
]


def main():
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        # Fetch existing codes to determine skips
        existing_codes = set(
            row[0]
            for row in conn.execute(
                text("SELECT category_code FROM risk_category WHERE category_code IS NOT NULL")
            ).fetchall()
        )

        to_insert = [
            {"code": code, "name": name}
            for code, name, _ in RISK_CATEGORIES
            if code not in existing_codes
        ]

        if to_insert:
            conn.execute(
                text("INSERT INTO risk_category (category_code, category_name) VALUES (:code, :name)"),
                to_insert,
            )

    inserted = len(to_insert)
    skipped = len(RISK_CATEGORIES) - inserted

    for item in to_insert:
        print(f"  [insert] {item['code']:20s}  {item['name']}")
    if skipped:
        print(f"  [skip]   {skipped} category(ies) already existed")

    print(f"\nDone. Inserted: {inserted}, Skipped: {skipped}")


if __name__ == "__main__":
    main()

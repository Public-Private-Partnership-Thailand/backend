"""
Seed script: bulk insert risk factor names into the `risk_factor` table.
Skips any factor whose factor_name already exists (idempotent).

Usage (from /home/ben/CU_PPP/backend):
    python scripts/seed_risk_factors.py
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

RISK_FACTORS = [
    "Access to the site and associated infrastructure",
    "Approval of designs",
    "Asset Ownership Risk (at the end of the contract)",
    "Availability of labor/materials",
    "Change in Contracting Authority ownership/status",
    "Change in law (and taxation)",
    "Change in Private Partner ownership",
    "Change of scope",
    "Changes in industrial code of practices",
    "Changes to design",
    "Climate change event",
    "Community and businesses",
    "Competition risk",
    "Compliance with applicable law",
    "Compliance with environmental consents and laws",
    "Condition At Handback Risk",
    "Condition of facility",
    "Conflicting or imperfect contract",
    "Considerations",
    "Consortium inability",
    "Contracting Authority default termination",
    "Contractor failure/Capability of SPV",
    "Contractual termination provisions",
    "Corruption and lack of respect for law",
    "Cost increases",
    "Cultural differences between main stakeholders",
    "Defects and defective materials",
    "Delay in approval / permit",
    "Delay in commencement of operations",
    "Delay in financial closure",
    "Delay in payment of anuity",
    "Different working methods/know-how between partners",
    "Disputes",
    "Disruptive Technology Risk",
    "Environmental conditions caused by the project",
    "Exchange rate fluctuation",
    "Existing asset condition",
    "External environmental events",
    "Financial attraction of project to investors",
    "Financiers unwilling to take high risk",
    "Fluctuation of material cost (by government)",
    "Fluctuation of material cost (by private)",
    "Force Majeure and Uninsurability termination",
    "Force majeure consequences",
    "Force majeure events",
    "Frequency of maintenance",
    "General principles",
    "Government support measures",
    "Health and safety compliance",
    "Heritage / indigenous land rights",
    "Heritage / indigenous people",
    "High bidding costs",
    "High finance cost",
    "High maintenance cost",
    "Higher demand than anticipated",
    "Inability to service debt",
    "Inadequate allocation of responsibility and risk",
    "Inadequate distribution of responsibility and risk",
    "Inadequate experience in PPP",
    "Inadequate feasibility study",
    "Inadequate law and supervision system",
    "Inadequate negotiation period prior to initiation",
    "Increased operating costs and affected performance",
    "Industrial action",
    "Inflation",
    "Insolvency/default of subcontractors and supplied",
    "insufficient income",
    "Intellectual property",
    "Interest rate fluctuation",
    "Interface",
    "Key planning consents",
    "Lack of commitment from public/private partner",
    "Lack of creditworthiness",
    "Lack of government guarantees",
    "Lack of transparency in the bidding",
    "Level of demand for the project",
    "Liability for death, personal injury, property damage and third party liability",
    "Low capacity of concession company",
    "Low operating productivity",
    "Lower demand than anticipated",
    "MAGA / Change in law termination",
    "Maintenance standards",
    "Market demand change",
    "Market forecast error",
    "Non-involvement of host-community",
    "Obtaining environmental consents",
    "Operational resources or input risk",
    "Organisation and coordination risk",
    "Performance/ price risk",
    "Permitted Contracting Authority step-in",
    "Political interference",
    "Political opposition",
    "Poor project appraisal and selection",
    "Poor public decision making process",
    "Poor quality of workmanship",
    "Pre-existing conditions",
    "Private Partner default termination",
    "Private Partner failure/insolvency",
    "Private Partner not to be fincially or technically capable implement the project.",
    "Project management and interface with other works/facilities",
    "Project operation change",
    "Protection of geological and historical objects",
    "Provision of permanent additional land",
    "Provision of required land - general",
    "Provision of temporary additional land",
    "Public Authority Delay Risk",
    "Public opposition to project",
    "Quality assurance and other construction regulatory standards",
    "Quality of operation",
    "Quality risk",
    "Refinancing",
    "Resettlement",
    "Residual assets risk",
    "Risk regarding pricing of product/service",
    "Site condition",
    "Site security",
    "Staff crises",
    "Strength of Contracting Authority payment covenant",
    "Sub-Contractor failure/insolvency",
    "Subjective project evaluation method",
    "Subsequent planning approvals",
    "Suitability of design",
    "Suitability of land",
    "Supporting incentive of government risk",
    "Tariff change",
    "Third party tort liability",
    "Timing of provision of required land",
    "Unavailability of insurance",
    "Unbalanced or inappropriate contractual terms",
    "Unclear about state participant portion",
    "Uncompetative tender",
    "Unfair process of selection of the private sector",
    "Unproven engineering techniques",
    "Unstable government",
    "Utilities and installations",
    "Vandalism",
    "Variations Risk",
    "Voluntary Termination by Contracting Authority",
    "Waste of materials",
    "Weather",
    "Works completion delays",
]


def main():
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        # Single bulk INSERT — uses PostgreSQL unnest() to expand the list,
        # then filters out names that already exist. All rows in one round-trip.
        result = conn.execute(
            text("""
                INSERT INTO risk_factor (factor_name)
                SELECT name
                FROM unnest(:names ::text[]) AS t(name)
                WHERE name NOT IN (
                    SELECT factor_name FROM risk_factor WHERE factor_name IS NOT NULL
                )
                RETURNING factor_name
            """),
            {"names": RISK_FACTORS},
        )
        inserted_rows = result.fetchall()

    inserted = len(inserted_rows)
    skipped = len(RISK_FACTORS) - inserted

    for row in inserted_rows:
        print(f"  [insert] {row[0]}")

    print(f"\nDone. Inserted: {inserted}, Skipped (already exists): {skipped}")


if __name__ == "__main__":
    main()

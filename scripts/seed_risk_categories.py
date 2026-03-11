"""
Seed script: bulk insert/update risk categories into the `risk_category` table.
Uses upsert (ON CONFLICT DO UPDATE) so running it again refreshes descriptions.

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

# (code, name, description_en, description_th)
RISK_CATEGORIES = [
    ("LAND_SITE", "Land availability, access & site",
     "The risk associated with selecting land suitable for the project; providing it with good title and free of encumbrances; addressing indigenous rights; obtaining necessary planning approvals; providing access to the site; site security; and site and existing asset condition.",
     "ความเสี่ยงที่เกี่ยวกับการได้มาซึ่งที่ดินที่เหมาะสม กรรมสิทธิ์ที่ดินที่ปราศจากภาระผูกพัน การจัดการสิทธิ์ชนพื้นเมือง การได้รับอนุมัติผังเมือง การเข้าถึงพื้นที่ ความปลอดภัยในพื้นที่ และสภาพสินทรัพย์เดิม"),
    ("SOCIAL", "Social",
     "The risk associated with the project impact on adjacent properties and affected people (including public protest and unrest); resettlement; indigenous land rights; and industrial action.",
     "ความเสี่ยงจากผลกระทบของโครงการต่อทรัพย์สินข้างเคียงและประชาชนที่ได้รับผลกระทบ รวมถึงการประท้วง การโยกย้ายถิ่นฐาน สิทธิ์ที่ดินชนพื้นเมือง และการนัดหยุดงาน"),
    ("ENVIRONMENTAL", "Environmental",
     "The risk associated with pre-existing conditions; obtaining consents; compliance with laws; conditions caused by the project; external events; and climate change.",
     "ความเสี่ยงด้านสิ่งแวดล้อม ได้แก่ สภาพแวดล้อมก่อนเริ่มโครงการ การได้รับความยินยอม การปฏิบัติตามกฎหมาย ผลกระทบจากโครงการ เหตุการณ์ภายนอก และการเปลี่ยนแปลงสภาพภูมิอากาศ"),
    ("DESIGN", "Design",
     "The risk that the project design is not suitable for the purpose required; approval of design; and changes.",
     "ความเสี่ยงที่การออกแบบโครงการไม่เหมาะสมกับวัตถุประสงค์ที่ต้องการ รวมถึงการขออนุมัติแบบและการเปลี่ยนแปลงแบบ"),
    ("CONSTRUCTION", "Construction",
     "The risk of construction costs exceeding modelled costs; completion delays; project management; interface; quality standards compliance; health and safety; defects; intellectual property rights compliance; industrial action; and vandalism.",
     "ความเสี่ยงด้านต้นทุนก่อสร้างที่เกินงบประมาณ ความล่าช้าในการแล้วเสร็จ การบริหารโครงการ การประสานงาน มาตรฐานคุณภาพ ความปลอดภัย ข้อบกพร่อง ทรัพย์สินทางปัญญา การนัดหยุดงาน และการก่อกวน"),
    ("VARIATIONS", "Variations",
     "The risk of changes requested by either party to the service which affect construction or operation.",
     "ความเสี่ยงจากการเปลี่ยนแปลงบริการที่ร้องขอโดยฝ่ายใดฝ่ายหนึ่ง ซึ่งส่งผลกระทบต่อการก่อสร้างหรือการดำเนินงาน"),
    ("OPERATING", "Operating",
     "The risk of events affecting performance or increasing costs beyond modelled costs; performance standards and price; availability of resources; intellectual property rights compliance; health and safety; compliance with maintenance standards; industrial action; and vandalism.",
     "ความเสี่ยงจากเหตุการณ์ที่กระทบต่อประสิทธิภาพหรือเพิ่มต้นทุนดำเนินงาน มาตรฐานการให้บริการและราคา ความพร้อมของทรัพยากร ทรัพย์สินทางปัญญา ความปลอดภัย มาตรฐานการบำรุงรักษา การนัดหยุดงาน และการก่อกวน"),
    ("DEMAND", "Demand",
     "The risk of traffic levels being different to forecast levels; the consequences for revenue and costs; and government support measures.",
     "ความเสี่ยงจากปริมาณการใช้บริการที่แตกต่างจากที่พยากรณ์ไว้ ผลกระทบต่อรายได้และต้นทุน รวมถึงมาตรการสนับสนุนของรัฐบาล"),
    ("FIN_MARKET", "Financial markets",
     "The risk of inflation; exchange rate fluctuation; interest rate fluctuation; unavailability of insurance; and refinancing.",
     "ความเสี่ยงด้านตลาดการเงิน ได้แก่ เงินเฟ้อ ความผันผวนของอัตราแลกเปลี่ยน ความผันผวนของอัตราดอกเบี้ย การขาดแคลนประกันภัย และการรีไฟแนนซ์"),
    ("STRATEGIC", "Strategic / Partnering",
     "The risk of the Private Partner and/or its sub-contractors not being the right choice to deliver the project; Contracting Authority intervention in the project; ownership changes; and disputes.",
     "ความเสี่ยงจากการเลือกพันธมิตรภาคเอกชนและผู้รับเหมาที่ไม่เหมาะสม การแทรกแซงของหน่วยงานรัฐ การเปลี่ยนแปลงกรรมสิทธิ์ และข้อพิพาท"),
    ("DISRUPT_TECH", "Disruptive technology",
     "The risk that a new emerging technology unexpectedly displaces an established technology or the risk of obsolescence of equipment or materials used.",
     "ความเสี่ยงจากเทคโนโลยีใหม่ที่เข้ามาแทนที่เทคโนโลยีที่ใช้อยู่โดยไม่คาดคิด หรือความล้าสมัยของอุปกรณ์และวัสดุที่ใช้ในโครงการ"),
    ("FORCE_MAJEURE", "Force majeure",
     "The risk that unexpected events occur that are beyond the control of the parties and delay or prevent performance.",
     "ความเสี่ยงจากเหตุการณ์ที่ไม่คาดคิดและอยู่นอกเหนือการควบคุมของคู่สัญญา ซึ่งอาจทำให้ล่าช้าหรือไม่สามารถปฏิบัติตามสัญญาได้"),
    ("POLITICAL", "Political",
     "Risks arising from government actions, policy changes, regulatory instability, or political interference that may affect project approvals, contractual conditions, or overall project continuity.",
     "ความเสี่ยงจากการดำเนินการของรัฐบาล การเปลี่ยนแปลงนโยบาย ความไม่แน่นอนของกฎระเบียบ หรือการแทรกแซงทางการเมืองที่ส่งผลต่อการอนุมัติโครงการและความต่อเนื่องโดยรวม"),
    ("LAW", "Law",
     "The risk of compliance with applicable law; and changes in law affecting performance of the project or the Private Partner's costs.",
     "ความเสี่ยงจากการไม่ปฏิบัติตามกฎหมายที่บังคับใช้ และการเปลี่ยนแปลงกฎหมายที่ส่งผลต่อการดำเนินโครงการหรือต้นทุนของเอกชนคู่สัญญา"),
    ("EARLY_TERMINATION", "Early termination",
     "The risk of a project being terminated before its natural expiry on various grounds; the financial consequences of such termination; and the strength of the Contracting Authority's payment covenant.",
     "ความเสี่ยงจากการยกเลิกโครงการก่อนกำหนดด้วยเหตุผลต่าง ๆ ผลกระทบทางการเงินจากการยกเลิก และความแข็งแกร่งของภาระผูกพันในการชำระเงินของหน่วยงานรัฐ"),
    ("HANDBACK_COND", "Condition at handback",
     "The risk of deterioration of the project assets/land during the life of the PPP and the risk that the project assets/land are not in the contractually required condition at the time of handback to the Contracting Authority.",
     "ความเสี่ยงจากการเสื่อมสภาพของสินทรัพย์หรือที่ดินโครงการตลอดอายุ PPP และความเสี่ยงที่สินทรัพย์จะไม่อยู่ในสภาพที่กำหนดตามสัญญาเมื่อถึงเวลาส่งคืนให้หน่วยงานรัฐ"),
    ("PROJECT_SELECTION", "Project selected",
     "Project selection refers to the process of choosing PPP projects that are socially acceptable, technically feasible, and aligned with public demand, where risks may arise from public opposition, inappropriate tendering, or poor assessment of project suitability.",
     "ความเสี่ยงในกระบวนการคัดเลือกโครงการ PPP ที่ต้องเป็นที่ยอมรับของสังคม มีความเป็นไปได้ทางเทคนิค และสอดคล้องกับความต้องการสาธารณะ โดยความเสี่ยงอาจเกิดจากการต่อต้านของประชาชน การประมูลที่ไม่เหมาะสม หรือการประเมินความเหมาะสมที่บกพร่อง"),
    ("RELATIONSHIP", "Relationship",
     "Relationship refers to the quality of collaboration, coordination, and mutual understanding between public and private partners in PPP projects, where differences in working methods, responsibilities, and communication can create significant risks.",
     "ความเสี่ยงด้านคุณภาพของความร่วมมือ การประสานงาน และความเข้าใจร่วมกันระหว่างภาครัฐและเอกชนใน PPP โดยความแตกต่างในวิธีการทำงาน ความรับผิดชอบ และการสื่อสาร อาจสร้างความเสี่ยงอย่างมีนัยสำคัญ"),
    ("PROJECT_FINANCE", "Project finance",
     "Project finance refers to the financial structure and attractiveness of a PPP project to investors, including the availability of financing, cost of capital, and the project's ability to generate sufficient returns to support long-term investment.",
     "ความเสี่ยงด้านโครงสร้างทางการเงินและความน่าดึงดูดของโครงการ PPP ต่อนักลงทุน รวมถึงความพร้อมของแหล่งเงินทุน ต้นทุนเงินทุน และความสามารถของโครงการในการสร้างผลตอบแทนเพียงพอเพื่อรองรับการลงทุนระยะยาว"),
    ("PROCUREMENT", "Procurement risks",
     "Risks related to the tendering and contracting process, including non-transparent selection procedures, uncompetitive bidding, poor negotiation, or delays in award decisions that may impact project performance and fairness.",
     "ความเสี่ยงในกระบวนการประมูลและการทำสัญญา รวมถึงขั้นตอนการคัดเลือกที่ขาดความโปร่งใส การประมูลที่ไม่มีการแข่งขัน การเจรจาที่ไม่มีประสิทธิภาพ หรือความล่าช้าในการตัดสินใจมอบสัญญา"),
]


def main():
    engine = create_engine(DATABASE_URL)

    inserted = 0
    updated = 0

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
                    RETURNING category_code, (xmax = 0) AS inserted
                """),
                {"code": code, "name": name, "desc_en": desc_en, "desc_th": desc_th},
            ).fetchone()
            action = "insert" if row[1] else "update"
            print(f"  [{action}] {row[0]}")
            if row[1]:
                inserted += 1
            else:
                updated += 1

    print(f"\nDone. Inserted: {inserted}, Updated: {updated}")


if __name__ == "__main__":
    main()

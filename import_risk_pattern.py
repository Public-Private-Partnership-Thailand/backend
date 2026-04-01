"""
Import risk_pattern data from CSV into the database.

CSV structure:
- Rows are risk factors grouped under risk categories
- Columns for phases: pre-construction, construction, operation (marked with ü)
- Columns for sources: GI hub, Yongjian Ke (China), Sy Tien Do (Vietnam), Nur Alkaf (Malaysia), SEPO Thailand
- Columns for thailand-otp projects: BTS Green line, MRT Blue line, MRT Purple line
"""
import os
import csv
import logging
from collections import defaultdict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlmodel import Session, select
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import (
    RiskCategory, RiskFactor, RiskPattern, RiskSource, RiskPhase
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_risk_patterns():
    csv_path = os.path.join(
        os.path.dirname(__file__),
        "โครงการร่วมลงทุนระหว่างรัฐและเอกชนในประเทศไทย-260212.xlsx - Risk factor.csv"
    )
    
    with Session(engine) as session:
        # 1. Load reference data
        categories = session.exec(select(RiskCategory).order_by(RiskCategory.risk_category_id)).all()
        cat_by_id = {c.risk_category_id: c for c in categories}
        
        factors = session.exec(select(RiskFactor)).all()
        factor_by_name = {f.factor_name.strip().lower(): f for f in factors}
        
        phases = session.exec(select(RiskPhase).order_by(RiskPhase.phase_id)).all()
        phase_bits = {p.phase_name: p.phase_id_from_bit_mask for p in phases}
        # pre-construction=1, construction=2, operation=4
        
        sources = session.exec(select(RiskSource).order_by(RiskSource.rs_id)).all()
        
        # 2. Create sources if they don't exist
        if not sources:
            logger.info("No risk sources found. Creating them...")
            source_data = [
                # Global sources
                {"rs_id": 1, "rs_id_from_bit_mask": 1, "meaning": "GI hub", "country": "global"},
                {"rs_id": 2, "rs_id_from_bit_mask": 2, "meaning": "Yongjian Ke et al. (China)", "country": "global"},
                {"rs_id": 3, "rs_id_from_bit_mask": 4, "meaning": "Sy Tien Do (Vietnam)", "country": "global"},
                {"rs_id": 4, "rs_id_from_bit_mask": 8, "meaning": "Nur Alkaf Abd Karim (Malaysia)", "country": "global"},
                # Thailand sources
                {"rs_id": 5, "rs_id_from_bit_mask": 16, "meaning": "SEPO", "country": "thailand"},
                # Thailand OTP (reports) - mapped to rs_id=6 for the bit mask
                {"rs_id": 6, "rs_id_from_bit_mask": 32, "meaning": "รายงาน สนข.", "country": "thailand"},
            ]
            for sd in source_data:
                src = RiskSource(**sd)
                session.add(src)
            session.commit()
            logger.info(f"Created {len(source_data)} risk sources")
            
            # Reload sources
            sources = session.exec(select(RiskSource).order_by(RiskSource.rs_id)).all()
        
        source_bit_map = {s.meaning: s.rs_id_from_bit_mask for s in sources}
        logger.info(f"Source bit map: {source_bit_map}")
        
        # Source column mapping from CSV
        # Col index 6: GI hub (global, bit=1)
        # Col index 7: Yongjian Ke (global, bit=2)
        # Col index 8: Sy Tien Do (global, bit=4)
        # Col index 9: Nur Alkaf (global, bit=8)
        # Col index 10: SEPO Thailand (thailand, bit=16)
        # Col index 11-13: BTS Green, MRT Blue, MRT Purple → treat as thailand OTP (bit=32)
        
        source_col_bits = {
            6: 1,   # GI hub
            7: 2,   # Yongjian Ke
            8: 4,   # Sy Tien Do
            9: 8,   # Nur Alkaf
            10: 16,  # SEPO
            11: 32,  # BTS Green line (รายงาน สนข.)
            12: 32,  # MRT Blue line (รายงาน สนข.)
            13: 32,  # MRT Purple line (รายงาน สนข.)
        }
        
        # Phase column mapping
        # Col index 3: pre-construction (bit=1)
        # Col index 4: construction (bit=2)
        # Col index 5: operation (bit=4)
        phase_col_bits = {
            3: 1,  # pre-construction
            4: 2,  # construction
            5: 4,  # operation
        }
        
        # 3. Parse CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Skip header rows (rows 0-6 are headers)
        # Data starts from row index 7 (line 8 in file)
        current_cat_id = None
        patterns_created = 0
        factors_created = 0
        skipped = 0
        
        for row_idx, row in enumerate(rows):
            if row_idx < 7:  # skip headers
                continue
            
            # Clean up row
            if len(row) < 7:
                continue
            
            no_col = row[0].strip() if row[0] else ""
            cat_col = row[1].strip().strip('"').strip() if row[1] else ""
            factor_col = row[2].strip().strip('"').strip() if row[2] else ""
            
            # Skip placeholder rows (...)
            if factor_col in ["…", "...", ""]:
                # But update category if there's a new one
                if no_col and no_col.isdigit():
                    current_cat_id = int(no_col)
                continue
            
            # Update current category if new one starts
            if no_col and no_col.isdigit():
                current_cat_id = int(no_col)
            
            if current_cat_id is None:
                continue
            
            # Find or create the factor
            factor_key = factor_col.strip().lower()
            factor_obj = factor_by_name.get(factor_key)
            
            if not factor_obj:
                # Try a fuzzy match by checking if factor starts with same text
                matched = False
                for existing_key, existing_fac in factor_by_name.items():
                    if existing_key.startswith(factor_key[:30]) or factor_key.startswith(existing_key[:30]):
                        factor_obj = existing_fac
                        matched = True
                        break
                
                if not matched:
                    # Create new factor
                    new_factor = RiskFactor(factor_name=factor_col.strip())
                    session.add(new_factor)
                    session.flush()
                    session.refresh(new_factor)
                    factor_obj = new_factor
                    factor_by_name[factor_key] = factor_obj
                    factors_created += 1
                    logger.info(f"Created new factor: {factor_col.strip()} (id={factor_obj.risk_factor_id})")
            
            # Calculate phase bitmask
            phase_bitmask = 0
            for col_idx, bit_val in phase_col_bits.items():
                if col_idx < len(row):
                    cell = row[col_idx].strip()
                    if cell and cell != "":
                        # ü or any non-empty means checked
                        phase_bitmask |= bit_val
            
            # Calculate source bitmask
            source_bitmask = 0
            for col_idx, bit_val in source_col_bits.items():
                if col_idx < len(row):
                    cell = row[col_idx].strip()
                    if cell and cell != "":
                        # l or any non-empty means checked
                        source_bitmask |= bit_val
            
            if phase_bitmask == 0 and source_bitmask == 0:
                skipped += 1
                continue
            
            # Check if pattern already exists
            existing = session.exec(
                select(RiskPattern).where(
                    RiskPattern.risk_category_id == current_cat_id,
                    RiskPattern.risk_factor_id == factor_obj.risk_factor_id
                )
            ).first()
            
            if existing:
                # Update existing pattern
                existing.phase = phase_bitmask
                existing.source = source_bitmask
                session.add(existing)
                logger.info(f"Updated pattern: cat={current_cat_id}, fac={factor_obj.risk_factor_id} ({factor_col[:30]}), phase={phase_bitmask}, source={source_bitmask}")
            else:
                # Create new pattern
                pattern = RiskPattern(
                    risk_category_id=current_cat_id,
                    risk_factor_id=factor_obj.risk_factor_id,
                    phase=phase_bitmask,
                    source=source_bitmask
                )
                session.add(pattern)
                logger.info(f"Created pattern: cat={current_cat_id}, fac={factor_obj.risk_factor_id} ({factor_col[:30]}), phase={phase_bitmask}, source={source_bitmask}")
            
            patterns_created += 1
        
        session.commit()
        logger.info(f"\n=== Import Complete ===")
        logger.info(f"Patterns created/updated: {patterns_created}")
        logger.info(f"New factors created: {factors_created}")
        logger.info(f"Rows skipped: {skipped}")


if __name__ == "__main__":
    import_risk_patterns()

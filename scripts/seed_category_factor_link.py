import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment / .env")

# Parsed from user request: (category_id, factor_id)
# Extract numbers from C001, F0104 => (1, 104)
DATA = [
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
    (20, 131), (20, 13), (20, 75), (20, 120), (20, 124), (20, 130), (20, 132), (20, 78)
]

def main():
    engine = create_engine(DATABASE_URL)

    inserted = 0

    with engine.begin() as conn:
        # clear existing data
        conn.execute(text("DELETE FROM category_factor_link"))
        
        for cat_id, fac_id in DATA:
            try:
                # Need to use try-except or ON CONFLICT, but we wiped it so we just Insert
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
                print(f"Error inserting {cat_id} -> {fac_id}: {e}")

    print(f"Done. Inserted {inserted} relations into category_factor_link.")

if __name__ == "__main__":
    main()

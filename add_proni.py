import os
import psycopg2
from dotenv import load_dotenv

def add_manufacturers():
    load_dotenv()
    db_url = os.getenv("DB_URL")
    if not db_url:
        print("❌ DB_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    manufacturers = [
        ("Proni", "Azienda forlivese con oltre mezzo secolo di esperienza nelle cialde e semilavorati."),
        ("Rubicone", "Produttore di semilavorati per gelateria e pasticceria dal 1959.")
    ]

    for name, desc in manufacturers:
        cur.execute(
            "INSERT INTO manufacturers (name, notes) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
            (name, desc)
        )
    
    conn.commit()
    print(f"✅ Added {len(manufacturers)} manufacturers.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_manufacturers()

import os
import sys
import psycopg2
from dotenv import load_dotenv

def import_sql_file(sql_file_path):
    load_dotenv()
    db_url = os.getenv("DB_URL")
    if not db_url:
        print("❌ DB_URL not found in .env")
        return

    if not os.path.exists(sql_file_path):
        print(f"❌ SQL file not found: {sql_file_path}")
        return

    print(f"🚀 Starting import of {sql_file_path}...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()

        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split into statements (basic split by semicolon)
        statements = sql_content.split(';')
        total = len(statements)
        
        print(f"📦 Found ~{total} statements to execute.")
        
        for i, stmt in enumerate(statements):
            stmt = stmt.strip()
            if not stmt:
                continue
            
            try:
                cur.execute(stmt)
            except Exception as e:
                # Most of these will be ON CONFLICT DO NOTHING anyway
                # but we print if it's not a duplicate key error
                if "duplicate key" not in str(e) and "already exists" not in str(e):
                    print(f"⚠️ Warning at statement {i}: {e}")
            
            if i % 100 == 0:
                print(f"  → Progress: {i}/{total} statements executed...")

        print(f"\n✅ Import of {sql_file_path} completed successfully!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_sql_file(sys.argv[1])
    else:
        # Default to Leagel if no arg
        import_sql_file("sql_output/leagel_2026.sql")

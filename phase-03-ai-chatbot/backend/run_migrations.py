"""Run database migrations for Phase 3 AI Chatbot."""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

# Migration files in order
migrations = [
    "migrations/add_conversations.sql",
    "migrations/add_messages.sql"
]

def run_migration(conn, migration_file):
    """Run a single migration file."""
    print(f"\nRunning migration: {migration_file}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
            print(f"[OK] Successfully executed: {migration_file}")
            return True
    except Exception as e:
        print(f"[ERROR] Error executing {migration_file}: {str(e)}")
        conn.rollback()
        return False

def main():
    """Run all migrations."""
    print("=" * 60)
    print("Database Migration Runner - Phase 3 AI Chatbot")
    print("=" * 60)
    print(f"\nConnecting to database...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("[OK] Connected to database successfully")

        success_count = 0
        for migration in migrations:
            if Path(migration).exists():
                if run_migration(conn, migration):
                    success_count += 1
            else:
                print(f"[WARNING] Migration file not found: {migration}")

        conn.close()

        print("\n" + "=" * 60)
        print(f"Migration Summary: {success_count}/{len(migrations)} successful")
        print("=" * 60)

        if success_count == len(migrations):
            print("\n[OK] All migrations completed successfully!")

            # Verify tables were created
            print("\nVerifying tables...")
            conn = psycopg2.connect(DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('conversations', 'messages')
                    ORDER BY table_name;
                """)
                tables = cur.fetchall()
                print(f"Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            conn.close()

            return 0
        else:
            print("\n[WARNING] Some migrations failed. Please check the errors above.")
            return 1

    except Exception as e:
        print(f"\n[ERROR] Database connection error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

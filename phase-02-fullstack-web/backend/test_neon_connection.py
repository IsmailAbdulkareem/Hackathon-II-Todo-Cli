"""
Test script to verify Neon PostgreSQL connection.
Run this to make sure your DATABASE_URL is correct.
"""

import sys
import os
from dotenv import load_dotenv

# Try to import required packages
try:
    import psycopg2
    from sqlalchemy import create_engine, text
except ImportError:
    print("ERROR: Missing required packages!")
    print("\nPlease install:")
    print("  pip install psycopg2-binary sqlalchemy python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get DATABASE_URL
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("ERROR: DATABASE_URL not found!")
    print("\nPlease set DATABASE_URL in your .env file or environment variables.")
    print("\nExample:")
    print("DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require")
    sys.exit(1)

print("Testing Neon PostgreSQL connection...")
print(f"Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'}")
print()

try:
    # Test connection with SQLAlchemy
    engine = create_engine(database_url)

    with engine.connect() as connection:
        # Test query
        result = connection.execute(text("SELECT version()"))
        version = result.fetchone()[0]

        print("SUCCESS: Connection successful!")
        print(f"PostgreSQL version: {version.split(',')[0]}")
        print()

        # Test creating a table
        print("Testing table creation...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        connection.commit()

        # Insert test data
        connection.execute(text("""
            INSERT INTO connection_test (test_message)
            VALUES ('Connection test successful!')
        """))
        connection.commit()

        # Query test data
        result = connection.execute(text("SELECT * FROM connection_test ORDER BY id DESC LIMIT 1"))
        row = result.fetchone()

        print(f"SUCCESS: Table created and data inserted!")
        print(f"Test message: {row[1]}")
        print(f"Created at: {row[2]}")
        print()

        # Clean up test table
        connection.execute(text("DROP TABLE connection_test"))
        connection.commit()

        print("SUCCESS: All tests passed!")
        print()
        print("Your Neon database is ready to use!")
        print()
        print("Next steps:")
        print("1. [DONE] Neon database configured")
        print("2. [NEXT] Deploy to Hugging Face Space")

except Exception as e:
    print("ERROR: Connection failed!")
    print(f"\nError: {str(e)}")
    print()
    print("Common issues:")
    print("1. Wrong DATABASE_URL format")
    print("2. Missing ?sslmode=require at the end")
    print("3. Incorrect username or password")
    print("4. Database not active in Neon Console")
    print()
    print("Please check your connection string and try again.")
    sys.exit(1)

"""
Fix database schema for conversations and messages tables
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        print("Checking current schema...")

        # Check if conversations table exists
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'conversations'
            ORDER BY ordinal_position;
        """)
        print("\nCurrent conversations table schema:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")

        # Drop and recreate conversations table with correct schema
        print("\nDropping conversations table...")
        cur.execute("DROP TABLE IF EXISTS messages CASCADE;")
        cur.execute("DROP TABLE IF EXISTS conversations CASCADE;")

        print("Creating conversations table with UUID...")
        cur.execute("""
            CREATE TABLE conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)

        print("Creating indexes for conversations...")
        cur.execute("CREATE INDEX idx_conversations_user_id ON conversations(user_id);")
        cur.execute("CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);")

        print("Creating messages table...")
        cur.execute("""
            CREATE TABLE messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)

        print("Creating indexes for messages...")
        cur.execute("CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);")
        cur.execute("CREATE INDEX idx_messages_created_at ON messages(created_at DESC);")

        conn.commit()
        print("\n✅ Schema fixed successfully!")

        # Verify new schema
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'conversations'
            ORDER BY ordinal_position;
        """)
        print("\nNew conversations table schema:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_schema()

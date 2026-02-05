"""Fix messages table to include user_id column"""
import sys
sys.path.insert(0, 'src')

from sqlmodel import Session, text
from src.core.database import engine

def fix_messages_table():
    with Session(engine) as session:
        try:
            print("Dropping messages table...")
            session.exec(text("DROP TABLE IF EXISTS messages CASCADE;"))

            print("Creating messages table with user_id...")
            session.exec(text("""
                CREATE TABLE messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL CHECK (LENGTH(content) <= 5000 AND LENGTH(TRIM(content)) > 0),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """))

            print("Creating indexes...")
            session.exec(text("CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);"))
            session.exec(text("CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);"))
            session.exec(text("CREATE INDEX idx_messages_user_id ON messages(user_id);"))

            session.commit()
            print("SUCCESS: Messages table fixed!")

            # Verify
            result = session.exec(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'messages'
                ORDER BY ordinal_position;
            """))
            print("\nMessages table schema:")
            for row in result:
                print(f"  {row[0]}: {row[1]}")

        except Exception as e:
            session.rollback()
            print(f"ERROR: {e}")
            raise

if __name__ == "__main__":
    fix_messages_table()


from app import create_app
from models import db

def migrate_banned_column():
    app = create_app()
    
    with app.app_context():
        # Add is_banned column if it doesn't exist
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0"))
                conn.commit()
                print("Successfully added is_banned column to users table")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("Column is_banned already exists")
                else:
                    print(f"Error: {e}")

if __name__ == '__main__':
    migrate_banned_column()

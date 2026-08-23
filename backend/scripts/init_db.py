import psycopg2
from urllib.parse import urlparse
from app.config import settings

def init_db():
    u = urlparse(settings.DATABASE_URL)
    db_name = u.path.lstrip('/')
    user = u.username or 'postgres'
    password = u.password or 'postgres'
    host = u.hostname or 'localhost'
    port = u.port or 5432

    print(f"Checking PostgreSQL at {host}:{port} with user '{user}'...")
    try:
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        if not exists:
            print(f"Database '{db_name}' not found. Creating '{db_name}'...")
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' successfully created!")
        else:
            print(f"Database '{db_name}' already exists.")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == '__main__':
    init_db()

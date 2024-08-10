from airflow import settings
from airflow.models import Connection
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import create_engine

def create_connection():
    conn = Connection(
        conn_id="postgres_conn",
        conn_type="Postgres",
        description="Connection for a Postgres DB",
        host="db",
        login="postgres",
        password="postgres",
        port=5432,
        schema="grillos"
    )

    session = settings.Session()  # Get the session
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()
    
    if not existing_conn:
        session.add(conn)
        session.commit()
        print(f"Connection {conn.conn_id} is created")
    else:
        print(f"Connection {conn.conn_id} already exists")

    session.close()

if __name__ == "__main__":
    create_connection()

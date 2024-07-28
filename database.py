import sqlite3
import pandas as pd

def get_db_connection(db_name='metadata.db'):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def create_database_from_csv(csv_file, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            year TEXT,
            keywords TEXT,
            main_finding TEXT,
            abstract TEXT,
            path TEXT
        )
    ''')
    conn.commit()

    df = pd.read_csv(csv_file)
    df.to_sql('pdf_metadata', conn, if_exists='append', index=False)
    conn.close()

def query_metadata(db_name='metadata.db'):
    conn = get_db_connection(db_name)
    metadata = conn.execute('SELECT * FROM pdf_metadata').fetchall()
    conn.close()
    return metadata

def get_metadata_by_id(metadata_id, db_name='metadata.db'):
    conn = get_db_connection(db_name)
    metadata = conn.execute('SELECT * FROM pdf_metadata WHERE id = ?', (metadata_id,)).fetchone()
    conn.close()
    return metadata

def filter_metadata(field, pattern, db_name='metadata.db'):
    conn = get_db_connection(db_name)
    query = f"SELECT * FROM pdf_metadata WHERE {field} LIKE ?"
    metadata = conn.execute(query, ('%' + pattern + '%',)).fetchall()
    conn.close()
    return metadata

def order_metadata(order_by, order_dir, db_name='metadata.db'):
    conn = get_db_connection(db_name)
    query = f"SELECT * FROM pdf_metadata ORDER BY {order_by} {order_dir}"
    metadata = conn.execute(query).fetchall()
    conn.close()
    return metadata

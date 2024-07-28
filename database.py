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
            cit TEXT,
            keywords TEXT,
            main_finding TEXT,
            abstract TEXT,
            path TEXT,
            subtopic TEXT,
            rq TEXT,
            color_flag TEXT DEFAULT '',
            ranking INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

    df = pd.read_csv(csv_file)
    df['color_flag'] = ''  # Initialize color_flag column
    df['ranking'] = 0      # Initialize ranking column
    df.to_sql('pdf_metadata', conn, if_exists='append', index=False)
    conn.close()

def query_metadata(db_name='metadata.db'):
    conn = get_db_connection(db_name)
    metadata = conn.execute('SELECT * FROM pdf_metadata').fetchall()
    conn.close()
    return metadata

def get_metadata_by_id(metadata_id, db_name='metadata.db'):
    conn = get_db_connection(db_name)

    # Get all column names from the table
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(pdf_metadata)")
    columns = [column[1] for column in cursor.fetchall()]

    # Build query to fetch all columns
    query = f"SELECT * FROM pdf_metadata WHERE id = ?"
    metadata = conn.execute(query, (metadata_id,)).fetchone()

    # Convert row object to dictionary
    metadata_dict = dict(metadata)

    conn.close()
    return metadata_dict


def filter_metadata(field, pattern, db_file):
    # Create connection and cursor
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Prepare the query
    query = f"SELECT * FROM pdf_metadata WHERE {field} LIKE ?"
    cursor.execute(query, (f'%{pattern}%',))

    # Fetch results
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    return [row_to_dict(row) for row in rows]


def order_metadata(order_by, order_dir, db_file):
    # Create connection and cursor
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Prepare the query based on the sorting criteria
    if order_by == 'parent_directory':
        # Calculate the parent directory dynamically
        query = """
            SELECT *, 
            substr(path, 1, length(path) - length(substr(path, instr(path, '/'), length(path)))) AS parent_directory 
            FROM pdf_metadata 
            ORDER BY parent_directory {} 
        """.format(order_dir)
    else:
        # Normal sorting
        query = f"SELECT * FROM pdf_metadata ORDER BY {order_by} {order_dir}"

    cursor.execute(query)

    # Fetch results
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    return [row_to_dict(row) for row in rows]


def update_color_flag(metadata_id, color_flag, db_name='metadata.db'):
    conn = get_db_connection(db_name)
    conn.execute('UPDATE pdf_metadata SET color_flag = ? WHERE id = ?', (color_flag, metadata_id))
    conn.commit()
    conn.close()

def update_star_ranking(metadata_id, ranking, db_name='metadata.db'):
    conn = get_db_connection(db_name)
    conn.execute('UPDATE pdf_metadata SET ranking = ? WHERE id = ?', (ranking, metadata_id))
    conn.commit()
    conn.close()


def add_key_value(metadata_id, key, value, db_name='metadata.db'):
    conn = get_db_connection(db_name)

    # Check if column exists
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(pdf_metadata)")
    columns = [column[1] for column in cursor.fetchall()]

    if key not in columns:
        conn.execute(f'ALTER TABLE pdf_metadata ADD COLUMN "{key}" TEXT')

    conn.execute(f'UPDATE pdf_metadata SET "{key}" = ? WHERE id = ?', (value, metadata_id))
    conn.commit()
    conn.close()

def row_to_dict(row):
    """Convert sqlite3.Row to a dictionary."""
    return dict(row)

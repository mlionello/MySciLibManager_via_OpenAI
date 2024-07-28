import sqlite3

def create_database(db_name):
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
    conn.close()


def insert_into_database(db_name, pdf_info_list):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for pdf_info in pdf_info_list:
        cursor.execute('''
            INSERT INTO pdf_metadata (title, authors, year, keywords, main_finding, abstract, path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pdf_info["Title"], pdf_info["Author(s)"], pdf_info["Year"], pdf_info["Keywords"], pdf_info["Main Finding"],
              pdf_info["One-sentence Abstract"], pdf_info["Path"]))
    conn.commit()
    conn.close()

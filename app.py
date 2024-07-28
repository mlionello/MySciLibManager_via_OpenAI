from flask import Flask, render_template, request, redirect, url_for
from database import create_database_from_csv, query_metadata, get_metadata_by_id
import argparse
import os

app = Flask(__name__)

@app.route('/')
def index():
    metadata = query_metadata()
    return render_template('index.html', metadata=metadata)

@app.route('/view/<int:metadata_id>')
def view(metadata_id):
    metadata = get_metadata_by_id(metadata_id)
    if metadata is None:
        return "Metadata not found!", 404
    return render_template('view.html', metadata=metadata)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask web application with SQLite database created from CSV file.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('--db_file', type=str, default='metadata.db', help='Name of the SQLite database file (default: metadata.db)')

    args = parser.parse_args()

    csv_file = args.csv_file
    db_file = args.db_file

    if not os.path.exists(db_file):
        create_database_from_csv(csv_file, db_file)

    app.run(debug=True)

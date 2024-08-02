import sqlite3
import webbrowser
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from database import create_database_from_csv, query_metadata, get_metadata_by_id, filter_metadata, order_metadata, \
    update_color_flag, update_star_ranking, row_to_dict, get_db_connection, add_key_value
import argparse
import os

app = Flask(__name__)
db_file = 'metadata.db'  # Default database file


@app.route('/files/<path:filename>')
def serve_file(filename):
    base_directory = '/'
    try:
        return send_from_directory(base_directory, filename)
    except FileNotFoundError:
        abort(404)


def add_parent_directory(metadata):
    for item in metadata:
        if isinstance(item, sqlite3.Row):
            item = row_to_dict(item)
        path = item.get('path', '')
        parent_dir = os.path.basename(os.path.dirname(path))
        item['parent_directory'] = parent_dir
    return metadata


@app.route('/', methods=['GET', 'POST'])
def index():
    order_by = request.args.get('order_by', 'id')
    order_dir = request.args.get('order_dir', 'ASC')

    if request.method == 'POST':
        field = request.form.get('field', 'title')
        pattern = request.form.get('pattern', '')
        metadata = filter_metadata(field, pattern, db_file)
    else:
        metadata = order_metadata(order_by, order_dir, db_file)

    metadata = add_parent_directory(metadata)

    return render_template('index.html', metadata=metadata, order_by=order_by, order_dir=order_dir)


@app.route('/update_flag', methods=['POST'])
def update_flag():
    metadata_id = request.form.get('metadata_id')
    color_flag = request.form.get('color_flag')
    update_color_flag(metadata_id, color_flag, db_file)
    return redirect(url_for('index'))


@app.route('/update_ranking', methods=['POST'])
def update_ranking():
    metadata_id = request.form.get('metadata_id')
    ranking = request.form.get('ranking')
    update_star_ranking(metadata_id, ranking, db_file)
    return redirect(url_for('index'))


@app.route('/view/<int:metadata_id>', methods=['GET', 'POST'])
def view(metadata_id):
    if request.method == 'POST':
        new_key = request.form.get('key')
        new_value = request.form.get('value')
        add_key_value(metadata_id, new_key, new_value, db_file)
        return redirect(url_for('view', metadata_id=metadata_id))

    metadata = get_metadata_by_id(metadata_id, db_file)
    if metadata is None:
        return "Metadata not found!", 404
    return render_template('view.html', metadata=metadata)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run Flask web application with SQLite database created from CSV file.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('--db_file', type=str, default='metadata.db',
                        help='Name of the SQLite database file (default: metadata.db)')

    args = parser.parse_args()
    csv_file = args.csv_file
    db_file = args.db_file

    if not os.path.exists(db_file):
        create_database_from_csv(csv_file, db_file)
    webbrowser.open_new('http://localhost:5000')
    app.run(debug=True)

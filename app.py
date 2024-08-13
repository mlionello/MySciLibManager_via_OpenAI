import argparse
import webbrowser

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import sqlite3
from config import DB_LABELS
from database import create_database_from_csv, query_metadata, get_metadata_by_id, filter_metadata, order_metadata, \
    update_color_flag, update_star_ranking, row_to_dict, get_db_connection, add_key_value
from main import collect_pdfs_info, save_to_csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
db_file = None  # Default database file

@app.route('/files/<path:filename>')
def serve_file(filename):
    base_directory = app.config['UPLOAD_FOLDER']
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
    global db_file

    order_by = request.args.get('order_by', 'id')
    order_dir = request.args.get('order_dir', 'ASC')

    if request.method == 'POST':
        field = request.form.get('field', 'title')
        pattern = request.form.get('pattern', '')
        metadata = filter_metadata(field, pattern, db_file)
        action = request.form.get('action')

        if action == 'load_db':
            if 'db_file' not in request.files:
                return "No file part", 400
            file = request.files['db_file']
            if file.filename == '':
                return "No selected file", 400
            if file and file.filename.endswith('.db'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                db_file = file_path
                return redirect(url_for('index'))
            return "Invalid file format. Please upload a .db file.", 400

        elif action == 'generate_db':
            if 'csv_file' not in request.files:
                return "No file part", 400
            file = request.files['csv_file']
            if file.filename == '':
                return "No selected file", 400
            if file and file.filename.endswith('.csv'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                db_file = os.path.splitext(file_path)[0] + '.db'
                create_database_from_csv(file_path, db_file)
                return redirect(url_for('index'))
            return "Invalid file format. Please upload a .csv file.", 400

        elif action == 'generate_csv':
            root_directory = request.form.get('folder_query')
            if os.path.isdir(root_directory):
                csv_file = os.path.join(root_directory, 'output.csv')
                log_file = os.path.join(root_directory, 'log.txt')
                existing_data = {}
                pdf_info_list, updated_data = collect_pdfs_info(root_directory, log_file, existing_data)
                save_to_csv(pdf_info_list, csv_file, updated_data)
                db_file = os.path.join(root_directory, 'output.db')
                create_database_from_csv(csv_file, db_file)
                return redirect(url_for('index'))
            return "Directory not found!", 404
    else:
        metadata = order_metadata(order_by, order_dir, db_file) if db_file else []

    metadata = add_parent_directory(metadata)
    static_fields = ['title', 'authors', 'year', 'cit', 'keywords', 'main_finding', 'abstract', 'path', 'color_flag',
                     'ranking']

    return render_template('index.html', metadata=metadata, order_by=order_by, order_dir=order_dir,
                           static_fields=static_fields, db_labels=DB_LABELS, db_file=db_file)

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
    # List of static fields that are known and should be handled explicitly
    static_fields = ['title', 'authors', 'year', 'keywords', 'main_finding', 'abstract', 'path', 'id', 'color_flag',
                     'ranking']

    return render_template('view.html', metadata=metadata, static_fields=static_fields)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run Flask web application with SQLite database created from CSV file.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('--db_file', type=str, default='metadata.db',
                        help='Name of the SQLite database file (default: metadata.db)')

    args = parser.parse_args()
    csv_file = args.csv_file
    db_file = args.db_file

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    webbrowser.open_new('http://localhost:5000')
    app.run(debug=True)

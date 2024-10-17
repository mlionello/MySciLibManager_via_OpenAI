import webbrowser

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
from config import DB_LABELS
from database import create_database_from_csv, get_metadata_by_id, filter_metadata, order_metadata, \
    update_color_flag, update_star_ranking, row_to_dict, add_key_value
from main import collect_pdfs_info, save_to_csv
import json


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
db_file = None  # Default database file

static_fields = ['Title', 'Citation', 'Keywords', 'Findings', 'ShortAbstract', 'color_flag', 'ranking']

@app.route('/files/<path:filename>')
def serve_file(filename):
    # Ensure that you use a base directory that is secure and appropriate for your application
    base_directory = '/'
    return send_from_directory(base_directory, filename)

@app.route('/progress')
def progress():
    try:
        with open('progress.json', 'r') as progress_file:
            progress = json.load(progress_file)
    except FileNotFoundError:
        progress = {'current': 0, 'total': 0}

    return progress

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
        action = request.form.get('action')

        # Handle the different actions
        if action == 'load_db':
            return handle_load_db()

        elif action == 'generate_db':
            return handle_generate_db()

        elif action == 'generate_csv':
            return handle_generate_csv()

        # Handle metadata filtering
        field = request.form.get('field', 'title')
        pattern = request.form.get('pattern', '')
        metadata = filter_metadata(field, pattern, db_file)
    else:
        metadata = order_metadata(order_by, order_dir, db_file) if db_file else []

    metadata = add_parent_directory(metadata)

    return render_template('index.html', metadata=metadata, order_by=order_by, order_dir=order_dir,
                           static_fields=static_fields, db_labels=DB_LABELS, db_file=db_file)


def handle_load_db():
    """Handles loading an existing database."""
    if 'db_file' not in request.files:
        return "No file part", 400
    file = request.files['db_file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.db'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        global db_file
        db_file = file_path
        return redirect(url_for('index'))
    return "Invalid file format. Please upload a .db file.", 400


def handle_generate_db():
    """Handles generating a database from a CSV file."""
    if 'csv_file' not in request.files:
        return "No file part", 400
    file = request.files['csv_file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        global db_file
        db_file = os.path.splitext(file_path)[0] + '.db'
        create_database_from_csv(file_path, db_file)
        return redirect(url_for('index'))
    return "Invalid file format. Please upload a .csv file.", 400


def handle_generate_csv():
    """Handles generating a CSV file from a directory and creating a database."""
    root_directory = request.form.get('folder_query')
    if os.path.isdir(root_directory):
        csv_file = os.path.join(root_directory, 'output.csv')
        log_file = os.path.join(root_directory, 'log.txt')
        existing_data = {}
        pdf_info_list, updated_data = collect_pdfs_info(root_directory, log_file, existing_data)
        save_to_csv(pdf_info_list, csv_file, updated_data)
        global db_file
        db_file = os.path.join(root_directory, 'output.db')
        create_database_from_csv(csv_file, db_file)
        return redirect(url_for('index'))
    return "Directory not found!", 404


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
    static_fields = ['Title', 'Citation', 'Keywords', 'Findings', 'ShortAbstract', 'color_flag', 'ranking']

    return render_template('view.html', metadata=metadata, static_fields=static_fields)


if __name__ == '__main__':

    csv_file = '/home/matteo/tmp_dataset.csv'
    db_file = ''

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    webbrowser.open_new('http://localhost:5000')
    app.run(debug=True)

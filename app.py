from flask import Flask, render_template, request, redirect, url_for
from database import create_database_from_csv, query_metadata, get_metadata_by_id, filter_metadata, order_metadata, update_color_flag, update_star_ranking
import argparse
import os

app = Flask(__name__)
db_file = 'metadata.db'  # Default database file

from flask import send_from_directory

@app.route('/files/<path:filename>')
def serve_file(filename):
    # Ensure that you use a base directory that is secure and appropriate for your application
    base_directory = '/'
    return send_from_directory(base_directory, filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        field = request.form['field']
        pattern = request.form['pattern']
        metadata = filter_metadata(field, pattern, db_file)
    else:
        order_by = request.args.get('order_by', 'id')
        order_dir = request.args.get('order_dir', 'ASC')
        metadata = order_metadata(order_by, order_dir, db_file)
    return render_template('index.html', metadata=metadata)

@app.route('/view/<int:metadata_id>')
def view(metadata_id):
    metadata = get_metadata_by_id(metadata_id, db_file)
    if metadata is None:
        return "Metadata not found!", 404
    return render_template('view.html', metadata=metadata)

@app.route('/update_flag', methods=['POST'])
def update_flag():
    metadata_id = request.form['metadata_id']
    color_flag = request.form['color_flag']
    update_color_flag(metadata_id, color_flag, db_file)
    return redirect(url_for('index'))

@app.route('/update_ranking', methods=['POST'])
def update_ranking():
    metadata_id = request.form['metadata_id']
    ranking = request.form['ranking']
    update_star_ranking(metadata_id, ranking, db_file)
    return redirect(url_for('index'))

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

from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection, query_metadata, get_metadata_by_id

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
    app.run(debug=True)

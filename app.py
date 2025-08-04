from flask import Flask, request, render_template, send_file
import os
from logic.duplicate_checker import analyze_test_cases
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file.filename.endswith(".xml"):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            report_path = analyze_test_cases(file_path)
            return send_file(report_path, as_attachment=True)
        return "Invalid file type. Only .xml is supported."
    return render_template("index.html")

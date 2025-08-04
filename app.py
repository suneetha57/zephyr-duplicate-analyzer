from flask import Flask, render_template, request, send_file
from logic.duplicate_checker import analyze_test_cases
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        xml_file = request.files['file']
        if xml_file:
            xml_path = os.path.join('uploads', xml_file.filename)
            os.makedirs('uploads', exist_ok=True)
            xml_file.save(xml_path)
            report_path = analyze_test_cases(xml_path)
            return send_file(report_path, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)

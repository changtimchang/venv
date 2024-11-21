from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
CORS(app)  # CORS 설정

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            # CSV 파일을 pandas로 읽어오기
            df = pd.read_csv(file_path)
            # 데이터의 첫 10개 행을 JSON 형식으로 반환
            return jsonify(df.head(10).to_dict(orient='records'))
        except Exception as e:
            print(f"Error while processing the file: {e}")
            return jsonify({'error': 'Error processing the file'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only CSV files are allowed.'}), 400

@app.route('/download_excel', methods=['GET'])
def download_excel():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
    
    try:
        df = pd.read_csv(file_path)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)

        return send_file(output, as_attachment=True, download_name="data.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    except Exception as e:
        print(f"Error while generating excel: {e}")
        return jsonify({'error': 'Error generating the Excel file'}), 500

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

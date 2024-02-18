import csv
import os
import requests
from flask import Flask, request, send_from_directory, render_template
import codecs
from nanonets import NANONETSOCR
from googletrans import Translator

app = Flask(__name__)

lib_version = 'b050b5bc-9848-11ee-9dcb-222020e1c43e'
translator = Translator()
model = NANONETSOCR()
model.set_token(lib_version)


def convert_csv_to_utf8(folder, input_file, output_file):
    input_file = os.path.join(folder, input_file)
    output_file = os.path.join(folder, output_file)

    with codecs.open(input_file, 'r', encoding='utf-8') as file:
        csvfile = csv.reader(file)
        rows = list(csvfile)

        with codecs.open(output_file, 'w', encoding='utf-8', errors='ignore') as utf8_csv_file:
            writer = csv.writer(utf8_csv_file)
            for row in rows:
                new_row = []
                for cell in row:
                    if cell == '':
                        new_row.append('')
                    else:
                        cell = cell.replace(".", "")
                        trans = translator.translate(str(cell)).text
                        new_row.append(trans)
                writer.writerow(new_row)


def image_to_csv(file_path, output_file_name):
    model.convert_to_csv(file_path, output_file_name=output_file_name)
    # convert_csv_to_utf8(upload_folder, output_file_name, translated_file)


translator = Translator()
UPLOAD_FOLDER = './'
FINAl_PROCESSED_FILE = 'final.csv'


def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isdir(file_path):
                continue
            if os.path.isfile(file_path) and (file_path.endswith('.py') or file_path.endswith(".html") or file_path.endswith('.md')):
                continue
            else:
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")


@app.route('/')
def index():
    return {'Heath-check': 'Service is running... !'}


@app.route('/file-processing')
def file_processing():
    return render_template('index.html')


@app.route('/extract-file', methods=['POST'])
def extract_file():
    if 'file' not in request.files:
        return 'No file provided'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    file_type = ''
    if file.filename.endswith('.csv'):
        file_type = 'CSV'
    elif file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
        file_type = 'IMAGE'
    elif file.filename.endswith('.pdf'):
        file_type = 'PDF'

    if file_type == '':
        return 'Uploaded file-type is not valid : {}'.format(file.filename)

    upload_folder = os.path.join(UPLOAD_FOLDER)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    delete_files_in_directory(UPLOAD_FOLDER)

    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    if file_type == 'IMAGE':
        # image_to_csv(upload_folder, file_path, 'output.csv', FINAl_PROCESSED_FILE)
        model.convert_to_csv(file_path, FINAl_PROCESSED_FILE)
    elif file_type == 'CSV':
        convert_csv_to_utf8(file.filename, FINAl_PROCESSED_FILE)
    elif file_type == 'PDF':
        model.convert_to_csv(file_path, FINAl_PROCESSED_FILE)

    # call_file_transfer(file_path, FINAl_PROCESSED_FILE)
    response = send_from_directory(UPLOAD_FOLDER, FINAl_PROCESSED_FILE)
    # return 'File uploaded: {}'.format(file.filename)
    return response


def call_file_transfer(file_path, file_name):
    url = "http://localhost:27017/api/v1/s3-upload/uploadFile"
    request_data = {
        "fileName": file_name
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, data=request_data, files=files)
    if response.status_code == 200:
        print("Successful Upload")
    else:
        print(f"Upload failed with status code: {response.status_code}")


@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = ''
    dest = 'en'
    src = 'auto'
    type = ''
    if 'text' not in data or data['text'] == '':
        return "Input text field is not valid"
    else:
        text = data['text']

    if 'dest' in data and data['dest'] != '':
        dest = data['dest']

    if 'src' in data and data['src'] != '':
        src = data['src']

    if 'type' in data and data['type'] != '':
        type = data['type']

    return translator.translate(text, dest, src).text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)

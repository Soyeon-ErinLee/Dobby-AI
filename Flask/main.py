from flask import Flask, render_template, request, session, redirect, url_for
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import Admin
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
import os
import sys
import time
import warnings
import json


warnings.filterwarnings("ignore")
basedir = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basedir, 'static/uploads')
upload_dir_2 = os.path.join(os.path.dirname(basedir), 'Data')
output_dir = os.path.join(basedir, 'output')
sys.path.append(os.path.join(os.path.dirname(basedir), 'Python_Modules'))
from _transcriber import TRANSCRIBER
from _file_transformer import SttTransformer
from make_tables import MAKE_TABLES

app = Flask(__name__)
app.debug = True

admin = Admin(name = 'Uploaded Files')
admin.init_app(app) 
dropzone = Dropzone(app)
admin.add_view(FileAdmin(upload_dir, name = 'FILES'))
app.config.from_pyfile('config.py')
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'audio/*, .mp3, .wav, .m4a'

transcriber = TRANSCRIBER()
front = None
model = None
with open(os.path.join(os.path.dirname(basedir), 'Data/faq_query.json')) as f:
    query_faq = json.load(f)

@app.route("/", methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        if f is not None:
            filename = secure_filename(f.filename)
            file_path = os.path.join(upload_dir, filename)
            f.save(file_path)
            session['audio_file_name'] = filename
            transcriber.upload(file_path, filename)
        else:
            session['num_speakers'] = request.form['speakers']
            return render_template('homepage.html', scroll = 'purpose')
    return render_template('homepage.html')

@app.route("/result", methods=['GET', 'POST'])
def result():
    path, file_type = transcribe()
    print("pass1")
    mtl = MAKE_TABLES(query_faq['query_dict_agenda'], model, types="Agenda")
    print("pass2")
    mtl.get_table()
    with open(os.path.join(basedir, "templates/result_agenda_1.html"), "r", encoding="UTF-8") as file:
        result_1 = file.read()
    with open(os.path.join(basedir, "templates/result_agenda_2.html"), "r", encoding="UTF-8") as file:
        result_2 = file.read()
    with open(os.path.join(basedir, "templates/result_agenda_3.html"), "r", encoding="UTF-8") as file:
        result_3 = file.read()
    with open(os.path.join(upload_dir_2, "Output.txt"), 'r', encoding="UTF-8") as file:
        txt = file.read()
    with open(os.path.join(upload_dir_2, "javascript.txt"), 'r', encoding="UTF-8") as file:
        txt2 = file.read()
    result_1 += front
    result_1 += result_2
    result_1 += txt
    result_1 += result_3
    result_1 += txt2
    result_1 += ("</body></html>")
    with open(os.path.join(basedir, "templates/final_result.html"), "w", encoding="UTF-8") as file:
        file.write(result_1)
    return render_template(
        'final_result.html', path = path, file_type = file_type
    )

@app.route("/result_interview", methods=['GET', 'POST'])
def result1():
    path, file_type = transcribe()
    with open(os.path.join(basedir, "templates/result_inter_1.html"), "r", encoding="UTF-8") as file:
        result_1 = file.read()
    with open(os.path.join(basedir, "templates/result_inter_2.html"), "r", encoding="UTF-8") as file:
        result_2 = file.read()
    with open(os.path.join(basedir, "templates/result_inter_3.html"), "r", encoding="UTF-8") as file:
        result_3 = file.read()
    with open(os.path.join(upload_dir_2, "interview_output.txt"), 'r', encoding="UTF-8") as file:
        txt = file.read()
    result_1 += front
    result_1 += result_2
    result_1 += txt
    result_1 += result_3
    with open(os.path.join(basedir, "templates/final_result.html"), "w", encoding="UTF-8") as file:
        file.write(result_1)
    return render_template(
        'final_result.html', path = path, file_type = file_type
    )

@app.route("/result_idea", methods=['GET', 'POST'])
def result2():
    path, file_type = transcribe()
    print("pass1")
    mtl = MAKE_TABLES(query_faq['query_dict_agenda'], model, types="Idea")
    print("pass2")
    mtl.get_table()
    with open(os.path.join(basedir, "templates/result_idea_1.html"), "r", encoding="UTF-8") as file:
        result_1 = file.read()
    with open(os.path.join(basedir, "templates/result_idea_2.html"), "r", encoding="UTF-8") as file:
        result_2 = file.read()
    with open(os.path.join(basedir, "templates/result_idea_3.html"), "r", encoding="UTF-8") as file:
        result_3 = file.read()
    with open(os.path.join(upload_dir_2, "Output.txt"), 'r', encoding="UTF-8") as file:
        txt = file.read()
    result_1 += front
    result_1 += result_2
    result_1 += txt
    result_1 += result_3
    with open(os.path.join(basedir, "templates/final_result.html"), "w", encoding="UTF-8") as file:
        file.write(result_1)
    return render_template(
        'final_result.html', path = path, file_type = file_type
    )

def transcribe():
    global front
    global model
    audio_file_name = session['audio_file_name']
    num_speakers = int(session['num_speakers'])
    session.clear()
    path = 'uploads/' + audio_file_name
    file_type = 'audio/' + audio_file_name.rsplit('.')[-1]
    data = transcriber.transcribe(num_speakers)
    current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    front = SttTransformer(data).html_transformer()  
    model = SttTransformer(data).model_transformer(current_time)
    return path, file_type


if __name__ == '__main__':
    app.run(host = '0.0.0.0')

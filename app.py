import os
from os.path import isfile, join
    
from flask import Flask, request, redirect, url_for, send_from_directory 
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads/'
RENDER_FOLDER = './renders/'
ALLOWED_EXTENSIONS = {'blend', 'txt'}

# upewnij sie ze folder ./uploads istnieje
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RENDER_FOLDER, exist_ok=True)

UPLOADED_FILES=[]
RENDERED_FILES={}

def list_files_in_directory(my_dir):
    return [f for f in os.listdir(my_dir) if isfile(join(my_dir, f))]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )                                   
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
        
        
    # wziete z https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    def is_blender_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST': # post - czyli user kliknal juz wyslanie pliku            
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file: # and is_blender_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                return redirect('/')
                #return redirect(url_for('uploaded_file',                                        filename=filename))   
        else: # GET - user odwiedza podstrone pierwszy raz
            tabela_istniejacych_plikow = "<table style='border: double;'><caption>Lista wrzuconych plikow:</caption><tr><th>plik zrodlowy</th><th>plik renderu</th></tr>"
            
            UPLOADED_FILES = list_files_in_directory(UPLOAD_FOLDER)
            
            for f in UPLOADED_FILES:
                tabela_istniejacych_plikow += "<td>" + f + "</td>" + \
                    "<td>puste</td></tr>";
            tabela_istniejacych_plikow += "</table>"
            return '''
                <!doctype html>
                <title>strona glowna</title>
                <h1>Upload new .blend file</h1>
                <form method=post enctype=multipart/form-data>
                  <input type=file name=file>
                  <input type=submit value=Upload>
                </form><br/>
                ''' + tabela_istniejacych_plikow
                                                    

    @app.route('/uploads/<filename>')
    def get_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
                               
    @app.route('/renders/<filename>')
    def get_rendered_file(filename):
        return send_from_directory(app.config['RENDER_FOLDER'],
                               filename)

    return app
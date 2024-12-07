from flask import Flask, jsonify, request, redirect, render_template, send_file, make_response
from flask_cors import CORS
from excel_treatment import ExcelConverterApp
import os
from psql_connector import PostgreSQLDao
from io import BytesIO
import pandas as pd
from excel_merger import process_excel_files
from datetime import datetime
from utils import delete_all_files_in_directory
from services import fetch_data_from_database, search_into_database, fetch_all_furbisher, get_classement, update_ranking

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}


pg_connection = PostgreSQLDao()
pg_connection.connect()

error_fetching_data = 'Une erreur est survenue lors de la collecte des données.'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assembleur')
def assembleur():
    return render_template('assembleur.html')

@app.route('/classement')
def classement():
    return render_template('classeur.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        file_processor = ExcelConverterApp()
        csv_file = file_processor.upload_and_convert(filename, pg_connection)
        if csv_file:
            return f'Fichier convertit avec success: {csv_file}'
        return 'Conversion du fichier échoué'
    return 'Invalid file format'


@app.route('/upload-catalogue', methods=['POST'])
def upload_catalogue_file():
    if 'files' not in request.files:
        return jsonify({"error": "Il manque un fichier"}), 400
    files = request.files.getlist('files')
    fournisseurs = request.form.getlist('fournisseurs')    
    if len(files) != len(fournisseurs):
        error_message = "Le nombre de ficher et de fournisseurs doivent être égaux"
        # Return a JSON blob response with the error
        response = make_response(jsonify({"error": error_message}), 400)
        response.headers['X-Error'] = error_message  # Include error in headers
        response.headers["Access-Control-Expose-Headers"] = "X-Error"
        return response

    file_paths = []
    for file in files:
        if file.filename == '':
            error_message = "Aucun fichier sélectionné"
            # Return a JSON blob response with the error
            response = make_response(jsonify({"error": error_message}), 400)
            response.headers['X-Error'] = error_message  # Include error in headers
            response.headers["Access-Control-Expose-Headers"] = "X-Error"
            return response
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            file_paths.append(file_path)
  # Process and combine the data
    try:
        combined_df = process_excel_files(file_paths, fournisseurs)
    except Exception as e:
        error_message = str(e)
        # Return a JSON blob response with the error
        response = make_response(jsonify({"error": error_message}), 400)
        response.headers['X-Error'] = error_message  # Include error in headers
        response.headers["Access-Control-Expose-Headers"] = "X-Error"
        return response
   
    current_date = datetime.now()
    # Formater la date (exemple : "YYYY-MM-DD HH:MM:SS")
    now = current_date.strftime('%d%m%Y')
    file_name =  "CATALOGUES_" + now
    # Create a BytesIO object to store the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        combined_df.to_excel(writer, index=False, sheet_name=file_name)
    output.seek(0)
    # Return the Excel file for direct download along with the file name
    response = send_file(
        output,
        as_attachment=True,
        download_name=file_name + ".xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Add the file name to the response headers
    response.headers["X-Filename"] = file_name + ".xlsx"
    
    delete_all_files_in_directory(app.config['UPLOAD_FOLDER'])    
    return response

    

@app.route('/update-classement', methods=['GET'])
def update_classement():
    id_rank = int(request.args.get('id', 0))
    classement = int(request.args.get('classement', 0))
    update_ranking(pg_connection, id_rank, classement) 
    return redirect('/classement')

@app.route('/search', methods=['GET'])  
def search():
    searched_words = str(request.args.get('libelle', ''))
    if searched_words != '':
        searched_words = searched_words.strip() 
    libelle = searched_words.upper()
    page = int(request.args.get('page', 1))
    rows_per_page = int(request.args.get('rows_per_page', 20))

    # Calculate the OFFSET for SQL query
    offset = (page - 1) * rows_per_page
    try:
        datas_fetched = search_into_database(pg_connection, libelle, rows_per_page, offset)
        data = datas_fetched['data']
        total_pages = datas_fetched['total_pages']
        
        # Return the paginated data as a JSON response
        return jsonify({
            'data': data,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error searching data:", e)
        return jsonify({'error': error_fetching_data}), 500



@app.route('/classement-furbisher', methods=['GET'])
def classement_furbisher():
    try:
        # SQL query to fetch data with LIMIT and OFFSET
        data = get_classement(pg_connection)
        # Return the paginated data as a JSON response
        return jsonify({
            'data': data
        })
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({'error': error_fetching_data}), 500


@app.route('/furbisher', methods=['GET'])
def furbisher():
    try:
        # SQL query to fetch data with LIMIT and OFFSET
        data = fetch_all_furbisher(pg_connection)
        # Return the paginated data as a JSON response
        return jsonify({
            'data': data
        })
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({'error': error_fetching_data}), 500
    
@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    # Get pagination parameters from the request
    page = int(request.args.get('page', 1))
    rows_per_page = int(request.args.get('rows_per_page', 20))
    # Calculate the OFFSET for SQL query
    offset = (page - 1) * rows_per_page
    
    # Slice the data for the current page
    try: 
        datas_fetched = fetch_data_from_database(pg_connection, rows_per_page, offset)
        data = datas_fetched['data']
        total_pages = datas_fetched['total_pages']

        # Return the paginated data as a JSON response
        return jsonify({
            'data': data,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({'error': 'An error occurred while fetching data.'}), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000)
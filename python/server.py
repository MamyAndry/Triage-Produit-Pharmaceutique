from flask import Flask, jsonify, request, redirect, render_template, send_file
from flask_cors import CORS
from excel_treatment import ExcelConverterApp
import os
from psql_connector import PostgreSQLConnection
from io import BytesIO
from excel_merger import *
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')

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
        csv_file = file_processor.upload_and_convert(filename)
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
        return jsonify({"error": "Le nombre de ficher et de fournisseurs doivent être égaux"}), 400

    file_paths = []
    for file in files:
        if file.filename == '':
            return jsonify({"error": "Aucun fichier sélectionné"}), 400
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            file_paths.append(file_path)
  # Process and combine the data
    combined_df = process_excel_files(file_paths, fournisseurs)
   
   
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
    
    return response
    

@app.route('/search', methods=['GET'])
def search():
    libelle = str(request.args.get('libelle', '')).upper()
    page = int(request.args.get('page', 1))
    rows_per_page = int(request.args.get('rows_per_page', 20))

    # Calculate the OFFSET for SQL query
    offset = (page - 1) * rows_per_page
    try:
        #Open connection to database
        pg_connection = PostgreSQLConnection()
        pg_connection.connect()
        
        # SQL query to fetch data with LIMIT and OFFSET
        query = "SELECT * FROM v_best_quality_price_ratio_product WHERE libelle LIKE '%s' LIMIT %d OFFSET %d"
        query = query % ("%" + libelle + "%", rows_per_page, offset)

        
        data = pg_connection.execute_query(query, fetch_results=True)

        # SQL query to get the total number of records
        count_query = "SELECT COUNT(*) FROM v_best_quality_price_ratio_product WHERE libelle LIKE '%s'" % ("%" + libelle + "%")
        total_records = pg_connection.execute_query(count_query, fetch_one=True, fetch_results=False)[0]
        total_pages = (total_records + rows_per_page - 1) // rows_per_page
        
        # Close the database connection
        pg_connection.close()
        # Return the paginated data as a JSON response
        return jsonify({
            'data': data,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({'error': 'An error occurred while fetching data.'}), 500

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    # Get pagination parameters from the request
    page = int(request.args.get('page', 1))
    rows_per_page = int(request.args.get('rows_per_page', 20))
    # Calculate the OFFSET for SQL query
    offset = (page - 1) * rows_per_page
    
    # Slice the data for the current page
    try:
        #Open connection to database
        pg_connection = PostgreSQLConnection()
        pg_connection.connect() 
        
        # SQL query to fetch data with LIMIT and OFFSET
        query = "SELECT * FROM catalogue LIMIT %s OFFSET %s" % (rows_per_page, offset)
        data = pg_connection.execute_query(query, fetch_results=True)

        # SQL query to get the total number of records
        count_query = "SELECT COUNT(libelle) FROM catalogue"
        total_records = pg_connection.execute_query(count_query, fetch_one=True, fetch_results=False)[0]
        print('total_records', total_records)

        total_pages = (total_records + rows_per_page - 1) // rows_per_page
        
        # Close the database connection
        pg_connection.close()
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
    app.run(debug=True)
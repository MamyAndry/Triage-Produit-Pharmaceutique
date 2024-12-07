def fetch_all_furbisher(connection):
    query = "SELECT nom FROM fournisseur"        
    data = connection.execute_query(query, fetch_results=True)
    return data

def get_classement(connection):
    query = "SELECT id, nom, classement FROM v_fournisseur_classement_lib"        
    data = connection.execute_query(query, fetch_results=True)
    return data

def update_ranking(connection, id, classement):
    query = "UPDATE fournisseur_classement SET classement = %d WHERE id = %d"
    query = query % (classement, id)        
    connection.execute_query(query, fetch_results=True)

def fetch_data_from_database(connection, rows_per_page, offset):
    # SQL query to fetch data with LIMIT and OFFSET
    query = "SELECT * FROM catalogue LIMIT %s OFFSET %s" % (rows_per_page, offset)
    data = connection.execute_query(query, fetch_results=True)

    # SQL query to get the total number of records
    count_query = "SELECT COUNT(libelle) FROM catalogue"
    total_records = connection.execute_query(count_query, fetch_one=True, fetch_results=False)[0]
    print('total_records', total_records)

    total_pages = (total_records + rows_per_page - 1) // rows_per_page
    return { 'data': data, 'total_pages': total_pages }

def search_into_database(connection, libelle, rows_per_page, offset):
    # SQL query to fetch data with LIMIT and OFFSET
    query = "SELECT fournisseur, libelle, PU, TVA, date_peremption FROM v_best_quality_price_ratio_product_by_frns WHERE libelle LIKE '%s' LIMIT %d OFFSET %d"
    query = query % ("%" +  libelle.replace(' ', '%%') + "%",  rows_per_page, offset)
    
    data = connection.execute_query(query, fetch_results=True)

    # SQL query to get the total number of records
    count_query = "SELECT COUNT(*) FROM v_best_quality_price_ratio_product_by_frns WHERE libelle LIKE '%s'" % ("%" + libelle.replace(' ', '%%') + "%")
    total_records = connection.execute_query(count_query, fetch_one=True, fetch_results=False)[0]
    total_pages = (total_records + rows_per_page - 1) // rows_per_page

    return { 'data': data, 'total_pages': total_pages }
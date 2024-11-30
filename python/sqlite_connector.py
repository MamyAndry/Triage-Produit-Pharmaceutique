import sqlite3
import csv

class SqliteDao:
    def __init__(self, db_name='pharmacie.db'):
        self.db_name = db_name

    def connect(self):
        """Establishes a connection to the Sqlite server."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print("Connection to Sqlite established successfully.")
            self.init_database()
            self.connection.commit()
        except Exception as error:
            print("Error while connecting to Sqlite:", error)

    def import_csv_to_catalogue(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Insert the data into the catalogue table
                self.cursor.execute('''
                    INSERT INTO catalogue (fournisseur, libelle, PU, TVA, date_peremption)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['fournisseur'], row['libelle'], row['PU'], row['TVA'], row['date_peremption']))
        
        # Commit the transaction to the database
        self.connection.commit()

    def execute_query(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def init_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS catalogue(
                fournisseur TEXT,
                libelle TEXT,
                PU DECIMAL(15, 4),
                TVA INTEGER,
                date_peremption DATE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fournisseur(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE
            )
        ''')

        self.cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_best_quality_product AS   
            SELECT * FROM catalogue ORDER BY date_peremption DESC
        ''')

        self.cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_best_quality_price_ratio_product AS   
            SELECT * FROM v_best_quality_product ORDER BY pu ASC
        ''')

    
    def close(self):
        """Closes the cursor and the connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Sqlite connection closed.")
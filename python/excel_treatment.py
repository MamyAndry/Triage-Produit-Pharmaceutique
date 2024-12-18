from psql_connector import PostgreSQLDao
from sqlite_connector import SqliteDao
import pandas as pd
import os
import unidecode

class ExcelConverterApp:

    def standardize_string(self, s):
        # Remove accents and convert to UTF-8 supported characters
        try:
            return unidecode.unidecode(s).encode('utf-8', 'ignore').decode('utf-8')
        except Exception as e:
            return None  # or handle in a specific way if needed
        
    def standardize_column(self, df, column_name):
        
        # Apply standardization to the specified column
        df[column_name] = df[column_name].apply(lambda x: self.standardize_string(x) if isinstance(x, str) else x)
        return df    
    
    def to_uppercase(self, df, column_name):
        # Apply str.upper() to convert all strings in the specified column to uppercase
        df[column_name] = df[column_name].apply(lambda x: x.upper() if isinstance(x, str) else x)
        return df

    def get_columns_to_delete(self, columns, columns_to_keep):
        columns_to_delete = list()
        for column in columns:
            if column not in columns_to_keep:
                columns_to_delete.append(column)
        return columns_to_delete

    def arrange_data_frame_columns(self, df, column_arrangement):
        rearranged_df = df[column_arrangement]  # Change the order as needed
        return rearranged_df
    
    def treat_dataframe(self, df, column_arrangement):
        columns = df.columns.tolist()
        columns_to_delete = self.get_columns_to_delete(columns, column_arrangement)
        treated_df = df.drop(columns=columns_to_delete, inplace=False)
        treated_df = self.arrange_data_frame_columns(treated_df, column_arrangement)
        # Drop rows where any NaN values are present
        treated_df = treated_df.dropna()
        return treated_df
                   
    def upload_and_convert(self, file_path, connection):
        df = self.read_excel(file_path)
        if df is not None:
            df = self.process_dataframe(df)
            csv_file = self.convert_to_csv(df, file_path)
            self.insert_into_db(csv_file, connection)
        return None 


    def read_excel(self, file_path):
        """
        Read the Excel file into a DataFrame.
        """
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None

    def rename_columns(self, df):
        """
        Rename columns in the DataFrame.
        """
        df = df.rename(columns={
            "FOURNISSEUR": "FOURNISSEURS",
            "P.U.": "PU",
            "D.P.": "DP",
            "T.V.A": "TVA",
            "T.V.A.": "TVA"
        })
        return df

    def process_tva(self, df):
        """
        Process the 'TVA' column.
        """
        df['TVA'] = df['TVA'].apply(lambda x: 1 if pd.isna(x) else x)
        df['TVA'] = df['TVA'].apply(lambda x: 1 if isinstance(x, str) and 'TVA' in x else 0)
        print(df['TVA'])
        return df

    def process_pu(self, df):
        """
        Process the 'PU' column.
        """
        df['PU'] = df['PU'].apply(lambda x: 0 if isinstance(x, str) else x)
        return df

    def process_dp(self, df):
        """
        Process the 'DP' column.
        """
        df['DP'] = pd.to_datetime(df['DP'], errors='coerce')
        df['DP'] = df['DP'].fillna("01-01-2150")
        return df

    def process_libelle(self, df):
        """
        Process the 'LIBELLE' column.
        """
        df['LIBELLE'] = df["LIBELLE"].replace('Ï', 'I', regex=True)
        df['LIBELLE'] = df['LIBELLE'].str.strip()
        df = self.standardize_column(df, "LIBELLE")
        df = self.to_uppercase(df, "LIBELLE")
        return df

    def process_dataframe(self, df):
        """
        Process the DataFrame by applying various transformations.
        """
        df = self.rename_columns(df)
        # df = self.process_tva(df)
        df = self.process_pu(df)
        df = self.process_dp(df)
        df = self.process_libelle(df)
        
        column_arrangement = ['FOURNISSEURS', 'LIBELLE', 'PU', 'TVA', 'DP']
        df = self.treat_dataframe(df, column_arrangement)
        return df


    def get_csv_filename(self, excel_file):
        """
        Convert the DataFrame to a CSV file and return the file path.
        """
        csv_file = excel_file.replace('.xlsx', '.csv')
        return csv_file

    def convert_to_csv(self, df, excel_file):
        try:
            # Specify the output directory
            output_dir = "uploads"
            
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the base name of the Excel file
            base_name = os.path.basename(excel_file)
            
            # Create the CSV filename
            csv_filename = os.path.splitext(base_name)[0] + '.csv'
            
            # Join the output directory and CSV filename to get the full path
            csv_file_path = os.path.join(output_dir, csv_filename)
            
            # Convert to CSV
            df.to_csv(csv_file_path, index=False)	
            os.remove(excel_file)	
            os.chmod(csv_file_path, 0o666)
            return csv_file_path
        except Exception as e:
            return None

    def insert_into_db(self, filename, db_connection):
        current_directory = os.getcwd()
        emplacement = os.path.join(current_directory, filename)
        truncate_query = "TRUNCATE catalogue"
        query = '''
            COPY catalogue
            FROM \'''' + emplacement + '''\'
            DELIMITER ',' 
            CSV HEADER
        '''
        update_query = '''
            CALL p_entree_fournisseur()
        '''
        truncate_query_result = db_connection.execute_query(truncate_query, fetch_results=False)
        query_result = db_connection.execute_query(query, fetch_results=False)
        update_query_result = db_connection.execute_query(update_query, fetch_results=False)
        print(truncate_query_result)
        print(query_result)
        print(update_query_result)
        os.remove(emplacement) 
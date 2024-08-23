import tkinter as tk
from tkinter import filedialog, messagebox
from psql_connector import PostgreSQLConnection
import pandas as pd
import os

class ExcelConverterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Excel to CSV Converter")
        self.master.geometry("300x150")

        self.converted_files = []

        self.upload_button = tk.Button(master, text="Upload and Convert Excel", command=self.upload_and_convert)
        self.upload_button.pack(pady=20)

        self.view_button = tk.Button(master, text="View Converted Files", command=self.view_list)
        self.view_button.pack(pady=20)

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
        return treated_df

    def upload_and_convert(self):
        excel_file = self.select_excel_file()
        if excel_file:
            df = self.read_excel(excel_file)
            if df is not None:
                df = df.rename(columns={
                    "FOURNISSEUR": "FOURNISSEURS",
                    "P.U.": "PU",
                    "D.P.": "DP",
                    "T.V.A": "TVA",
                    "T.V.A.": "TVA"
                })
                df['TVA'] = df['TVA'].apply(lambda x: 1 if x == 'TVA' else x)
                df['TVA'] = df['TVA'].fillna(0)
                column_arrangement = ['FOURNISSEURS', 'LIBELLE', 'PU', 'TVA', 'DP']
                df = self.treat_dataframe(df, column_arrangement)
                csv_file = self.convert_to_csv(df, excel_file)
                if csv_file:
                    self.converted_files.append(csv_file)
                    messagebox.showinfo("Success", f"File converted successfully: {csv_file}")

    def select_excel_file(self):
        excel_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not excel_file:
            messagebox.showinfo("Info", "No file selected.")
            return None
        return excel_file

    def read_excel(self, excel_file):
        try:
            df = pd.read_excel(excel_file)
            return df
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the Excel file: {str(e)}")
            return None

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
            
            return csv_file_path
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while converting to CSV: {str(e)}")
            return None

    def view_list(self):
        if not self.converted_files:
            messagebox.showinfo("Info", "No files have been converted yet.")
        else:
            files_list = "\n".join(self.converted_files)
            messagebox.showinfo("Converted Files", f"Converted files:\n\n{files_list}")

    def insert_into_db(self, filename):
        current_directory = os.getcwd()
        query = '''
            COPY catalogue
            FROM ''' + current_directory + '/uploads/' + filename + '''
            DELIMITER ',' 
            CSV HEADER
        '''
        # Connection parameters
        host = "your_host"
        database = "your_database"
        user = "mamisoa                                                                           "
        password = "your_password"
        port = 5432

        pg_connection = PostgreSQLConnection(host, database, user, password, port)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()
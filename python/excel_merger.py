import pandas as pd
import glob

import pandas as pd
import glob

# Function to identify the header row and reset the dataframe with correct headers
def identify_and_reset_header(df):
    # Check if there are any "Unnamed" columns
    if any("Unnamed" in str(col) for col in df.columns):
        # Iterate over rows to find the valid header row
        for idx, row in df.iterrows():
            if row.notnull().sum() > 2:  # Assume a valid header has more than 2 non-null values
                df.columns = df.iloc[idx]  # Reset the header to this row
                df = df.drop(index=list(range(idx + 1)))  # Drop rows before the actual data
                break
    return df

def filter_sheets_by_name(sheet_names):
    # Filter only sheets containing "list" or "produit"
    return [sheet for sheet in sheet_names if 'list' in sheet.lower() or 'produit' in sheet.lower() or 'dispo' in sheet.lower()]

def check_if_column_contains_words(col, list):
    for word in list:
        if word in col.lower():
            return True
    return False

# Function to extract the relevant columns (libelle/designation, Prix/PU, Date peremption)
def extract_relevant_columns(df):
    columns_to_extract = [
        next(col for col in df.columns if check_if_column_contains_words(col, ['libelle', 'libell2', 'designation', 'désignation', 'denomination', 'dénomination']) is True),
        next(col for col in df.columns if check_if_column_contains_words(col, ['prix', 'pu', 'p.u']) is True),
        next(col for col in df.columns if check_if_column_contains_words(col, ['date', 'peremption', 'per', 'dp']) is True),
        next(col for col in df.columns if check_if_column_contains_words(col, ['tva', 'taxe', 'obs']) is True)
    ]
    return df[columns_to_extract]

# Function to extract and unify relevant columns (libelle/designation, Prix/PU, Date peremption)
def extract_and_unify_columns(df):    
    # Convert column names to lowercase for easier matching
    df.columns = df.columns.str.lower()
    
    # Define a mapping from possible column names to unified names
    column_mapping = {
        'libellé': 'LIBELLE',
        'libelle': 'LIBELLE',
        'designation': 'LIBELLE',
        'désignation': 'LIBELLE',
        'dénomination': 'LIBELLE',
        'denomination': 'LIBELLE',
        'prix': 'PU',
        'pu': 'PU',
        'p.v': 'PU',
        'pv': 'PU',
        'p.u': 'PU',
        'date': 'DP',
        'peremption': 'DP',
        'dp': 'DP',
        'tva': 'TVA',
        'obs': 'TVA',
        'observation': 'TVA',
        'obrservation': 'TVA'
    }
    
    # Initialize a DataFrame with standardized column names
    unified_df = pd.DataFrame(columns=['LIBELLE', 'PU', 'TVA', 'DP'])
    
    # Extract and map the relevant columns
    for original_col, unified_col in column_mapping.items():
        if original_col in df.columns:
            unified_df[unified_col] = df[original_col]
    
    # Return the unified DataFrame with extracted data
    return unified_df

# Function to clean the dataframe by dropping rows where at least 2 columns are null
def clean_dataframe(df):
    return df.dropna(thresh=2)

# Function to process a single Excel file (read all sheets, extract, and clean)
def process_excel_file(file_path):
    xls = pd.ExcelFile(file_path)
    file_data = []
    relevant_sheets = filter_sheets_by_name(xls.sheet_names)
    
    for sheet_name in relevant_sheets:
        print(sheet_name, " ", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print('----------AVANT\n' , df)
        df = identify_and_reset_header(df)
        print('----------APRES\n' , df)
        df = extract_and_unify_columns(df)
        df = clean_dataframe(df)
        file_data.append(df)
    
    return pd.concat(file_data, ignore_index=True)

def process_excel_files(file_paths, fournisseurs):
    combined_data = []
    
    for file_path, fournisseur in zip(file_paths, fournisseurs):
        xls = pd.ExcelFile(file_path)
        relevant_sheets = filter_sheets_by_name(xls.sheet_names)
        
        for sheet_name in relevant_sheets:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = identify_and_reset_header(df)
            df = extract_and_unify_columns(df)
            df = clean_dataframe(df)
                
            # Add fournisseur column
            df['FOURNISSEUR'] = fournisseur
            
            combined_data.append(df)
    
    return pd.concat(combined_data, ignore_index=True) if combined_data else pd.DataFrame()

# Main function to process multiple Excel files and combine them into one
def combine_excel_files(file_paths):
    combined_data = []
    for file_path in file_paths:
        processed_df = process_excel_file(file_path)
        combined_data.append(processed_df)
    return pd.concat(combined_data, ignore_index=True)

# Function to export the final combined dataframe to Excel
def export_combined_data(df, output_file):
    df.to_excel(output_file, index=False)
    print(f"All Excel files combined, filtered, and saved as '{output_file}'.")

# Main execution
if __name__ == "__main__":
    # # List of Excel files (adjust path accordingly)
    # excel_files = glob.glob("E:\\PHARMACIE\\catalogue\\*.xlsx")  # Adjust path accordingly
    
    # # Combine all files
    # combined_df = combine_excel_files(excel_files)
    
    # # Export the combined data
    # export_combined_data(combined_df, "combined_output.xlsx")

    try:
        file_paths = [
            "E:\\PHARMACIE\\catalogue\\CATALOGUE UBIPHARM PCIE 20 SEPTEMBRE 2024.xlsx", 
            "E:\\PHARMACIE\\catalogue\\CatalogueSOPHARMADDU06août2024.xls", 
            "E:\\PHARMACIE\\catalogue\\DISPONIBLE 20092024.xls"
        ]
        fournisseurs = [
            "UBIPHARM",
            "SOPHARMAD",
            "INTERPHARMA SARL"
        ]
        
        # Process and combine the data
        combined_df = process_excel_files(file_paths, fournisseurs)
        
        # Export the combined data to an Excel file
        export_combined_data(combined_df, "combined_output_with_fournisseur.xlsx")
    
    except Exception as e:
        print(e)

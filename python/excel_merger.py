import pandas as pd
import os
import pandas as pd
import glob

# Function to identify the header row and reset the dataframe with correct headers
def identify_and_reset_header(df):
    # Check if there are any "Unnamed" columns
    print("-------------VIERGE--------------\n", df)
    unnamed_count = sum(1 for col in df.columns if "Unnamed" in str(col))
    if unnamed_count > 1:
        for idx, row in df.iterrows():
            if row.notnull().sum() > 2:  # Assume a valid header has more than 2 non-null values
                df.columns = df.iloc[idx]  # Reset the header to this row
                df = df.drop(index=list(range(idx + 1)))  # Drop rows before the actual data
                break
    return df

def filter_sheets_by_name(sheet_names):
    if len(sheet_names) == 1:
        return sheet_names
    return [sheet for sheet in sheet_names if 'list' in sheet.lower() or 'produit' in sheet.lower() or 'dispo' in sheet.lower() or 'catalogue'  in sheet.lower()]

def check_if_column_contains_words(col, list):
    for word in list:
        if word in col.lower():
            return True
    return False

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
        'péremption': 'DP',
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
        # Check if any of the columns contains the original_col as a substring
        matching_columns = [col for col in df.columns if original_col in str(col)]
        if matching_columns:
            unified_df[unified_col] = df[matching_columns[0]]  # Taking the first match
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
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = identify_and_reset_header(df)
        df = extract_and_unify_columns(df)
        df = clean_dataframe(df)
        file_data.append(df)
    return pd.concat(file_data, ignore_index=True)

def process_excel_files(file_paths, fournisseurs):
    combined_data = []
    
    for file_path, fournisseur in zip(file_paths, fournisseurs):
        xls = pd.ExcelFile(file_path)
        relevant_sheets = filter_sheets_by_name(xls.sheet_names)
        print(relevant_sheets)
        for sheet_name in relevant_sheets:
            print("FOURNISSEUR = ", fournisseur)
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = identify_and_reset_header(df)
            print("----------AVANT----------------\n", df)
            df = extract_and_unify_columns(df)
            print("----------APRES----------------\n", df)
            df = clean_dataframe(df)
            if df.empty:
                raise ValueError(f"Lors de la combinaison des excels, une erreur est survenue sur l'excel du fournisseur: {fournisseur}")
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


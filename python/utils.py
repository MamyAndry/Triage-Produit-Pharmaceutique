import os
import shutil

def delete_all_files_in_directory(directory_path):
    # Check if the directory exists
    if os.path.exists(directory_path):
        # Iterate over each file in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                # Check if it's a file and remove it
                if os.path.isfile(file_path):
                    os.remove(file_path)
                # If it's a directory, remove it recursively
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        print(f"Directory {directory_path} does not exist")

# def search_query(search_term):
#     search_terms = search_term.split()
#     for elt in search_terms:

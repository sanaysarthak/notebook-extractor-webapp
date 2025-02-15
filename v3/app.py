import os
import nbformat
import re
import zipfile
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure outputs directory exists
OUTPUT_FOLDER = 'Outputs'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Function to sanitize folder names by removing invalid characters
def sanitize_folder_name(folder_name):
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized_name = re.sub(invalid_chars, '', folder_name)
    return sanitized_name

# Function to extract code cells
def extract_code_cells(notebook_file_path):
    try:
        with open(notebook_file_path, 'r', encoding='utf-8') as notebook_file:
            notebook_content = nbformat.read(notebook_file, as_version=4)
        code_cells = [cell.source for cell in notebook_content.cells if cell.cell_type == 'code']
        return code_cells
    except Exception as e:
        return str(e)

# Function to save code cells to files
def save_code_cells_to_files(code_cells, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for index, code in enumerate(code_cells, start=1):
        file_path = os.path.join(output_folder, f"code_cell_{index}.py")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(code)
    return len(code_cells)

# Function to delete uploaded files
def delete_uploaded_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting the file {file_path}: {e}")

# Function to create a ZIP file containing the extracted .py files
def create_zip_from_folder(folder_path, zip_filename):
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        notebook_file = request.files['notebook_file']
        if notebook_file:
            # Save the file to the uploads folder
            file_path = os.path.join(UPLOAD_FOLDER, notebook_file.filename)
            notebook_file.save(file_path)

            # Extract the base filename to use for folder naming
            base_filename = os.path.splitext(notebook_file.filename)[0]
            sanitized_folder_name = sanitize_folder_name(base_filename)
            output_folder = os.path.join(OUTPUT_FOLDER, sanitized_folder_name)

            # Extract code cells from the notebook
            code_cells = extract_code_cells(file_path)
            if isinstance(code_cells, str):  # Error handling
                return render_template('index.html', error=code_cells)
            
            # Save code cells to .py files
            total_cells = save_code_cells_to_files(code_cells, output_folder)

            # Delete the uploaded file after processing
            delete_uploaded_file(file_path)

            # Create a ZIP file containing the extracted code cells
            zip_filename = f"{sanitized_folder_name}.zip"
            zip_file_path = create_zip_from_folder(output_folder, zip_filename)

            # Return success message and the download link for the ZIP file
            return render_template('index.html', message=f"{total_cells} code cells were extracted and saved.",
                                   zip_file_path=zip_file_path)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    # Serve the zip file for download
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

import os
import time
import zipfile
import shutil
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import nbformat
from threading import Thread  # Importing Thread to run background task
from flask import jsonify  # Import jsonify to send JSON responses

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to sanitize folder name
def sanitize_folder_name(folder_name):
    return folder_name.replace(" ", "_").replace(",", "_")

# Function to extract code cells and save them to files
def extract_code_cells(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
            notebook_content = nbformat.read(notebook_file, as_version=4)
        code_cells = []
        for cell in notebook_content.cells:
            if cell.cell_type == 'code':
                code_cells.append(cell.source)
        return code_cells
    except Exception as e:
        print(f"Error: {e}")
        return []

# Function to create a ZIP file
def create_zip(output_folder):
    zip_file_path = os.path.join(OUTPUT_FOLDER, f"{os.path.basename(output_folder)}.zip")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_folder))
    return zip_file_path

# Function to delete extracted code cells and output folder
def delete_output_folder(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

# Function to delete uploaded file
def delete_uploaded_file(upload_path):
    if os.path.exists(upload_path):
        os.remove(upload_path)

# Function to delete everything in the outputs folder after 10 seconds
def delete_all_files_in_output():
    # Wait for 1 second before deleting files
    time.sleep(1)

    # Delete everything inside the OUTPUT_FOLDER
    for filename in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Delete subdirectories
        else:
            os.remove(file_path)  # Delete files

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload and extraction
        file = request.files['notebook_file']
        
        if file:
            filename = secure_filename(file.filename)
            notebook_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file to the uploads directory
            file.save(notebook_path)

            base_filename = os.path.splitext(filename)[0]
            sanitized_folder_name = sanitize_folder_name(base_filename)
            output_folder = os.path.join(app.config['OUTPUT_FOLDER'], sanitized_folder_name)

            # Extract code cells and save to output folder
            code_cells = extract_code_cells(notebook_path)
            if code_cells:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                for index, code in enumerate(code_cells, start=1):
                    file_path = os.path.join(output_folder, f"code_cell_{index}.py")
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(code)

                # Create ZIP file after extraction
                zip_file_path = create_zip(output_folder)

                # Delete the uploaded notebook file after ZIP is created
                delete_uploaded_file(notebook_path)

                # Start the background task to delete everything inside the OUTPUT_FOLDER after 10 seconds
                Thread(target=delete_all_files_in_output).start()

                # Return success message and ZIP file path to frontend in JSON format
                return jsonify({
                    "message": f"{len(code_cells)} code cells were extracted and saved.",
                    "zip_file_path": zip_file_path.split('/')[-1]
                })
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    # Serve the ZIP file for download
    zip_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(zip_file_path):
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    return "File not found", 404

@app.route('/cleanup', methods=['POST'])
def cleanup():
    # This function will delete everything inside the outputs folder after download is confirmed
    delete_all_files_in_output()

    return jsonify({"status": "success", "message": "Files deleted after download."})

if __name__ == '__main__':
    app.run(debug=True)

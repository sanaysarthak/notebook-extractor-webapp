import os
import zipfile
import shutil
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import nbformat

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'Outputs'

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

                # Return success message and ZIP file path to frontend
                return render_template('index.html', message=f"{len(code_cells)} code cells were extracted and saved.",
                                       zip_file_path=zip_file_path.split('/')[-1], folder_name=sanitized_folder_name)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    # Serve the ZIP file for download
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    # This function will delete the extracted files after download is confirmed.
    folder_name = request.json.get('folder_name')
    output_folder = os.path.join(app.config['OUTPUT_FOLDER'], folder_name)
    delete_output_folder(output_folder)
    return jsonify({"status": "success", "message": "Files deleted after download."})

if __name__ == '__main__':
    app.run(debug=True)

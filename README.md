<a id="readme-top"></a>

<br />
  <h1 align="center">Jupyter Notebook Code Extractor Web App</h1>

<p align="center">
  <strong>The web app is now live and can be accessed at:</strong>  <a href="https://notebook-extractor.vercel.app/">notebook-extractor.app</a>
  
</p>
  <p align="center">
    It allows a user extract all code cells from a Jupyter Notebook file and save each one of them as an individual .py file.
  </p>
</div>

<p align="center">
  <img src="https://github.com/user-attachments/assets/8c1c1e5c-2453-49a2-8547-a70c3e044ec4" alt="webapp-screenshot"/>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#overview">Overview</a>
    </li>
    <li>
      <a href="#run-locally">Run Locally</a>
    </li>
    <li>
      <a href="#how-to-use">How to Use</a>
    </li>
    <li>
      <a href="#libraries-used">Libraries Used</a>
    </li>
  </ol>
</details>



<!--OVERVIEW --> 
<a id="overview"></a>
## Overview :-

This project allows users to easily upload a Jupyter notebook file through a web interface. The app extracts all code cells from the notebook and saves each code cell as a separate Python script (```.py```) file. The code cells are organized and saved in a user-friendly way, allowing users to download them in a ZIP archive.

Key features include:
- Web interface for uploading notebook files.
- Automatic extraction of code cells from the notebook.
- Download the extracted code cells as separate ```.py``` files in a ZIP archive.
- Error handling and progress indication during the extraction process.



<!--SETUP -->
<a id="run-locally"></a>
## Run Locally :-

#### Prerequisites
- Python 3.x installed on your machine.
- ```pip``` for installing dependencies

#### Installing Dependencies
1. Clone or download this repository to your local machine.
  ```sh
  git clone https://github.com/sanaysarthak/notebook-extractor-webapp.git
  ```
2. Navigate to the project directory.
  ```sh
   cd notebook-extractor-webapp
  ```
3. Install the required dependencies by running the following command in your terminal.
  ```sh
  pip install -r requirements.txt
  ```



<!-- HOW TO USE -->
<a id="how-to-use"></a>
## How to Use :-

#### Step 1: Run the Web App
In the project folder, start the web app by running the following command:
```sh
python app.py
```

#### Step 2: Access the Web Interface
Open your browser and navigate to http://127.0.0.1:5000. This will load the web interface of the app.

#### Step 3: Upload the Jupyter Notebook File
Click the "Upload" button and select your Jupyter notebook (e.g., .ipynb file) from your local machine.

#### Step 4: Wait for the Extraction to Complete
The app will extract all code cells from the notebook, and you will see a progress message during the extraction.

#### Step 5: Download the Extracted Code Cells
Once extraction is complete, you'll get a link to download the Python code cells as a ZIP file, with each cell saved as a separate ```.py``` file.



<!--LIBRARIES-USED -->
<a id="libraries-used"></a>
## Libraries Used :-

This project requires the following Python dependencies:

- ```Flask``` - For creating the web app.
- ```nbformat``` - To read and process Jupyter notebook files.
- ```os``` - For file handling and directory management (standard Python library).
- ```zipfile``` - To create the ZIP archive containing the extracted code cells.
- ```re``` - For sanitizing folder names (standard Python library).

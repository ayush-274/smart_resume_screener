# app.py

import os
import pdfplumber  # <-- NEW IMPORT
from flask import Flask, jsonify, request

# Create an 'uploads' directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- NEW HELPER FUNCTION ---
def extract_text_from_file(file_path):
    """
    Extracts text from a given file (supports .pdf and .txt).
    """
    if file_path.endswith('.pdf'):
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            return f"Error reading PDF file: {e}"
    elif file_path.endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading TXT file: {e}"
    else:
        return "Unsupported file type."

# Define the /health endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is up and running!"}), 200

# Define the /upload endpoint
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Missing resume or job description file"}), 400

    resume_file = request.files['resume']
    jd_file = request.files['job_description']

    if resume_file.filename == '' or jd_file.filename == '':
        return jsonify({"error": "One or both files are empty"}), 400

    # Save the files
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
    jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_file.filename)
    
    resume_file.save(resume_path)
    jd_file.save(jd_path)
    
    # --- MODIFIED PART: EXTRACT TEXT AFTER SAVING ---
    resume_text = extract_text_from_file(resume_path)
    jd_text = extract_text_from_file(jd_path)
    
    return jsonify({
        "status": "success",
        "message": "Files uploaded and text extracted successfully",
        "resume_text": resume_text[:500] + "...", # Return a snippet for preview
        "jd_text": jd_text[:500] + "..."      # Return a snippet for preview
    }), 200

# Main entry point for the application
if __name__ == '__main__':
    app.run(debug=True)
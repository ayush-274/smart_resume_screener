# app.py

import os
import pdfplumber
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy # <-- NEW IMPORT

# Initialize the Flask application
app = Flask(__name__)

# --- NEW DATABASE CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# --- NEW DATABASE MODEL ---
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    # We will add more fields like score and justification later
    
    def __repr__(self):
        return f'<Candidate {self.filename}>'

# Create an 'uploads' directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is up and running!"}), 200

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Missing resume or job description file"}), 400

    resume_file = request.files['resume']
    # We'll use the job description text later in Phase 3
    # jd_file = request.files['job_description'] 
    
    if resume_file.filename == '':
        return jsonify({"error": "Resume file is empty"}), 400

    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
    resume_file.save(resume_path)
    
    resume_text = extract_text_from_file(resume_path)
    
    # --- MODIFIED PART: SAVE TO DATABASE ---
    try:
        new_candidate = Candidate(filename=resume_file.filename, resume_text=resume_text)
        db.session.add(new_candidate)
        db.session.commit()
        candidate_id = new_candidate.id
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    return jsonify({
        "status": "success",
        "message": f"Candidate '{resume_file.filename}' added to database.",
        "candidate_id": candidate_id
    }), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database table if it doesn't exist
    app.run(debug=True)
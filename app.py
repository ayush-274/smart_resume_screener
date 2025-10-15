# app.py

import os
import pdfplumber
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy # <-- NEW IMPORT
from llm_service import extract_structured_data, score_resume_against_jd # <-- MODIFIED IMPORT


# Initialize the Flask application
app = Flask(__name__)

# --- NEW DATABASE CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# --- NEW DATABASE MODEL ---
# app.py -> inside the Candidate class definition

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    education = db.Column(db.String(255), nullable=True)
    # --- NEW FIELDS ---
    match_score = db.Column(db.Integer, nullable=True)
    justification = db.Column(db.Text, nullable=True)
    
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
    jd_file = request.files['job_description'] # <-- UNCOMMENTED THIS
    
    if resume_file.filename == '' or jd_file.filename == '':
        return jsonify({"error": "One or both files are empty"}), 400

    # Save files
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
    jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_file.filename)
    resume_file.save(resume_path)
    jd_file.save(jd_path)
    
    # Extract text from both files
    resume_text = extract_text_from_file(resume_path)
    jd_text = extract_text_from_file(jd_path)
    
    # --- NEW: CALL BOTH LLM FUNCTIONS ---
    structured_data = extract_structured_data(resume_text)
    scoring_data = score_resume_against_jd(resume_text, jd_text)
    
    try:
        new_candidate = Candidate(
            filename=resume_file.filename,
            resume_text=resume_text,
            skills=', '.join(structured_data.get('skills', [])),
            experience_years=structured_data.get('experience_years', 0),
            education=structured_data.get('education', 'Not found'),
            # --- SAVE NEW SCORING DATA ---
            match_score=scoring_data.get('score', 0),
            justification=scoring_data.get('justification', 'N/A')
        )
        db.session.add(new_candidate)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    return jsonify({
        "status": "success",
        "message": f"Candidate '{resume_file.filename}' processed, scored, and saved.",
        "candidate_id": new_candidate.id,
        "extracted_data": structured_data,
        "match_analysis": scoring_data # <-- ADDED ANALYSIS TO RESPONSE
    }), 201

@app.route('/shortlist', methods=['GET'])
def get_shortlisted_candidates():
    """
    Retrieves all candidates from the database, sorted by match score.
    """
    try:
        # Query all candidates and order them by match_score in descending order
        candidates = Candidate.query.order_by(Candidate.match_score.desc()).all()
        
        # Create a list of dictionaries to be returned as JSON
        candidate_list = []
        for candidate in candidates:
            candidate_data = {
                "id": candidate.id,
                "filename": candidate.filename,
                "score": candidate.match_score,
                "justification": candidate.justification,
                "skills": candidate.skills,
                "experience_years": candidate.experience_years,
                "education": candidate.education
            }
            candidate_list.append(candidate_data)
            
        return jsonify(candidate_list), 200
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Main entry point for the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

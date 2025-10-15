# llm_service.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-latest')

# --- NEW: Define safety settings to be less restrictive ---
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

def extract_structured_data(resume_text):
    # ... (prompt is the same)
    prompt = f"""
    Based on the following resume text, extract the key skills, total years of professional experience, 
    and the highest level of education.

    Format the output as a JSON object with the following keys: 'skills', 'experience_years', 'education'.
    
    - 'skills' should be a list of strings.
    - 'experience_years' should be an integer.
    - 'education' should be a string describing the highest degree and field of study.

    Resume Text:
    ---
    {resume_text}
    ---
    """
    
    try:
        # --- MODIFIED: Added safety_settings to the call ---
        response = model.generate_content(prompt, safety_settings=safety_settings)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"An error occurred during LLM processing (extract_structured_data): {e}")
        return { "skills": [], "experience_years": 0, "education": "Not found" }

def score_resume_against_jd(resume_text, jd_text):
    # ... (prompt is the same)
    prompt = f"""
    Compare the following resume with this job description and provide a fit rating and justification.
    The fit rating should be an integer between 1 and 10, where 1 is a very poor fit and 10 is an excellent fit.
    The justification should be a brief, 2-3 sentence explanation of why you gave that rating, highlighting key strengths or weaknesses.

    Format the output as a single JSON object with two keys: 'score' and 'justification'.

    Resume Text:
    ---
    {resume_text}
    ---

    Job Description:
    ---
    {jd_text}
    ---
    """
    
    try:
        # --- MODIFIED: Added safety_settings to the call ---
        response = model.generate_content(prompt, safety_settings=safety_settings)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"An error occurred during LLM scoring (score_resume_against_jd): {e}")
        return { "score": 0, "justification": "Error during processing." }
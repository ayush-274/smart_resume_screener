# Smart Resume Screener

## Objective
[cite_start]This project is designed to intelligently parse resumes, extract key information like skills and experience, and score them against a given job description using a Large Language Model (LLM)[cite: 2, 3].

## Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLite with Flask-SQLAlchemy
- **LLM:** Google Gemini API via `google-generativeai`
- **PDF Parsing:** `pdfplumber`

## Architecture
The application is a monolithic Flask server with a modular service for LLM interactions.
- `app.py`: Contains the main Flask application, API endpoint definitions (`/health`, `/upload`, `/shortlist`), and the database models.
- `llm_service.py`: Handles all communication with the Google Gemini API, containing separate functions for structured data extraction and for scoring/justification.
- `project.db`: A SQLite database file that stores all candidate information.
- `uploads/`: A directory where uploaded resumes and job descriptions are temporarily stored.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd smart-resume-screener
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create the environment file:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```
    GOOGLE_API_KEY="your-api-key-here"
    ```
5.  **Run the application:**
    ```bash
    python app.py
    ```
    The server will start on `http://127.0.0.1:5000`.

## API Endpoints

- **`POST /upload`**: Uploads a resume and job description. It processes the files, scores the candidate, and saves the data to the database.
- **`GET /shortlist`**: Retrieves a ranked list of all candidates, sorted from the highest score to the lowest.

## LLM Prompts Used

**1. For Structured Data Extraction:**
```
<-- Copy and paste the prompt from your extract_structured_data function here -->
```

**2. For Scoring and Justification:**
```
<-- Copy and paste the prompt from your score_resume_against_jd function here -->
```

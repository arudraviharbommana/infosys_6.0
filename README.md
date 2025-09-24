# AI-Free Skill Matcher

A full-stack application designed to intelligently match resumes with job descriptions using a sophisticated rule-based engine. This project provides a detailed analysis of skill alignment, identifies gaps, and offers actionable recommendations without relying on external AI models.

## 🌟 Core Features

- **Full-Stack Architecture**: Robust Python (Flask) backend and a dynamic React frontend.
- **Dual Input System**: Supports both text input and file uploads (PDF, TXT) for resumes and job descriptions.
- **Advanced PDF Parsing**: Extracts text from PDF files on the backend using `PyPDF2` and `pdfplumber`.
- **Rule-Based Skill Engine**:
    - **Custom Skill Extractor**: Identifies skills from text using a comprehensive, categorized database.
    - **Intelligent Job Matcher**: Calculates a match score based on skill overlap, experience, and category alignment.
    - **Detailed Comparison View**: Generates a side-by-side table comparing resume skills to job requirements, highlighting exact and weak matches.
- **Actionable Recommendations**: Provides a prioritized list of missing skills to guide learning and development.
- **Modern Frontend**:
    - **React-based SPA**: A responsive and interactive user interface.
    - **Dynamic Results Visualization**: Displays match scores, skill breakdowns, and comparison tables in a clear, user-friendly format.
    - **3D Animated UI**: An engaging background powered by Three.js.
- **Secure Authentication**: A simple and effective user login system.

## 🛠 Technology Stack

- **Backend**:
    - **Python 3**: Core programming language.
    - **Flask**: Web framework for the REST API.
    - **Flask-CORS**: Handles cross-origin requests from the frontend.
    - **PyPDF2 & pdfplumber**: Libraries for robust PDF text extraction.
- **Frontend**:
    - **React**: For building the user interface.
    - **Three.js & @react-three/fiber**: For the 3D animated background.
    - **CSS**: Custom styling for a modern look and feel.
- **Development & Deployment**:
    - **Node.js/npm**: For frontend dependency management and development server.
    - **pip**: For Python package management.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ and pip
- Node.js and npm

### Backend Setup
1.  Navigate to the backend directory:
    ```bash
    cd new_resume/backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the Flask server:
    ```bash
    python app.py
    ```
    The backend will be running at `http://127.0.0.1:5000`.

### Frontend Setup
1.  In a new terminal, navigate to the frontend directory:
    ```bash
    cd new_resume/frontend
    ```
2.  Install npm packages:
    ```bash
    npm install
    ```
3.  Start the React development server:
    ```bash
    npm start
    ```
    The frontend will open automatically in your browser at `http://localhost:3000`.

## 📁 Project Structure

```
/new_resume
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthForm.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── SkillMatcherDashboard.jsx  # Main UI for matching
│   │   │   └── ThreeDScene.jsx
│   │   ├── styles/
│   │   │   └── main.css
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── ...
└── custom_ai.py            # Core rule-based skill matching logic
```

## 🎯 How It Works

1.  **Input**: The user provides their resume and a job description via text input or file upload on the React frontend.
2.  **Processing**: The frontend sends the data to the Flask backend. If files are uploaded, the backend extracts the text.
3.  **Analysis**: The `custom_ai.py` module is used to:
    - Extract skills, experience, and categories from both the resume and the job description.
    - Compare the two sets of data to find matched, missing, and extra skills.
    - Generate a detailed comparison table showing exact and weak matches.
4.  **Scoring**: A comprehensive `overall_score` is calculated based on weighted factors like skill overlap, confidence, and experience.
5.  **Recommendations**: A list of learning recommendations is generated based on high-priority missing skills.
6.  **Output**: The backend returns a JSON object with the complete analysis, which the frontend then displays in a structured and intuitive results view.

---

**Built with a focus on transparent, rule-based analysis for effective career development.**
# SkillMatcher Project Workflow

## Overview
SkillMatcher is a full-stack application for AI-powered resume analysis and career guidance. It consists of a React frontend, a Flask backend, and a MongoDB database (running in Docker). The system enables users to register/login, analyze their resumes against job descriptions, and view their analysis history.

---

## 1. User Registration & Login
- **Frontend:**
  - User accesses the app and is presented with login/signup forms.
    - On form submission, a POST request is sent to the backend `/user` endpoint with the user's email and username.
    - **Backend:**
      - Receives the request, checks if the user exists in the `users` collection in MongoDB.
        - If the user does not exist, creates a new user document.
          - Responds with user data (email, username).
          - **Frontend:**
            - Stores user session (in memory or localStorage).
              - Navigates to the dashboard.

              ---

              ## 2. Resume & Job Description Analysis
              - **Frontend:**
                - User uploads a resume (PDF or text) and pastes a job description.
                  - On analysis, sends a POST request to `/analyze` with resume text, JD text, and user email.
                  - **Backend:**
                    - Extracts skills from both resume and JD using NLP (spaCy).
                      - Compares skills, calculates match score, and generates recommendations.
                        - Stores the analysis result in the `analysis_history` collection, linked to the user's email.
                          - Responds with analysis results (matched skills, missing skills, extra skills, recommendations, score).
                          - **Frontend:**
                            - Displays the analysis results to the user in the dashboard.

                            ---

                            ## 3. Viewing Analysis History
                            - **Frontend:**
                              - User navigates to the History page.
                                - Sends a GET request to `/history?email=...`.
                                - **Backend:**
                                  - Fetches all analysis records for that user from the `analysis_history` collection.
                                    - Responds with the user's analysis history.
                                    - **Frontend:**
                                      - Displays the list of past analyses and their results.

                                      ---

                                      ## 4. Database (MongoDB)
                                      - **Collections:**
                                        - `users`: Stores user accounts (email, username).
                                          - `analysis_history`: Stores each analysis (resume skills, JD skills, matched/missing/extra skills, recommendations, score, email).
                                          - **Persistence:**
                                            - All user and analysis data is persistent and user-specific.

                                            ---

                                            ## 5. Backend (Flask)
                                            - **Endpoints:**
                                              - `/user` (POST): Register or login a user.
                                                - `/analyze` (POST): Analyze resume and JD, store and return results.
                                                  - `/history` (GET): Fetch analysis history for a user.
                                                    - `/extract_skills`, `/match_skills`, `/suggest_skills`, `/extract_resume_text`, `/skills_list`: Utility endpoints for skill extraction and suggestions.
                                                    - **Database Connection:**
                                                      - Connects to MongoDB (Docker) at `mongodb://localhost:27017/`.
                                                        - Handles all business logic and data storage/retrieval.

                                                        ---

                                                        ## 6. Frontend (React)
                                                        - **Features:**
                                                          - User authentication (login/signup).
                                                            - Resume and JD input (PDF upload or manual text).
                                                              - Analysis dashboard with results display.
                                                                - History page for past analyses.
                                                                - **API Calls:**
                                                                  - Uses a configurable `API_BASE_URL` for all backend requests.
                                                                    - Handles session management and navigation.

                                                                    ---

                                                                    ## 7. Deployment & Environment
                                                                    - **MongoDB:**
                                                                      - Runs in a Docker container, accessible at `localhost:27017`.
                                                                      - **Backend:**
                                                                        - Flask app runs on port 5000, accessible to the frontend.
                                                                        - **Frontend:**
                                                                          - React app runs on port 3000 (or as configured), communicates with backend via API.
                                                                            - In cloud/dev environments, set `REACT_APP_API_BASE_URL` to the backend's public URL.

                                                                            ---

                                                                            ## 8. Data Flow Summary
                                                                            1. User logs in or signs up (data stored in MongoDB).
                                                                            2. User uploads resume and JD, runs analysis (results stored in MongoDB).
                                                                            3. User views analysis results and history (data fetched from MongoDB).

                                                                            All data flows through the backend, ensuring security, persistence, and user-specific experience.

                                                                            ---

                                                                            ## 9. Extensibility
                                                                            - Add more endpoints for advanced analytics or admin features.
                                                                            - Integrate additional NLP models or skill databases.
                                                                            - Enhance frontend UI/UX for better user experience.

                                                                            ---

**End of Workflow**

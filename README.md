# AI Study Buddy — Class 12 Streamlit Capstone

A multi-page Streamlit study companion with:
- Dashboard
- Subject-wise MCQ quizzes (Physics, Chemistry, Mathematics, Biology, Computer Science)
- Weekly study planner
- Notes creator and downloads
- Quiz performance charts and CSV export

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The app creates `study_buddy_data/quiz_progress.json` locally to retain quiz history.
The question bank is a small sample for demonstration and should be checked against your current syllabus.

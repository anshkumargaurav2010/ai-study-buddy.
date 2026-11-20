import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, datetime
import plotly.express as px

st.set_page_config(
    page_title="AI Study Buddy | Class 12",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path("study_buddy_data")
DATA_DIR.mkdir(exist_ok=True)
PROGRESS_FILE = DATA_DIR / "quiz_progress.json"

st.markdown("""
<style>
    .main {background: #f7f8fc;}
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #4338ca);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {color: white; margin-bottom: .2rem;}
    .hero p {color: #e0e7ff; margin-bottom: 0;}
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e5e7eb;
        padding: 14px; border-radius: 14px;
    }
    .small-muted {color: #64748b; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_progress(records):
    PROGRESS_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

QUESTION_BANK = {
    "Physics": [
        {"q": "What is the SI unit of capacitance?", "options": ["Ohm", "Farad", "Henry", "Volt"], "answer": "Farad", "why": "Capacitance is measured in farads (F)."},
        {"q": "The time constant of an RC circuit is:", "options": ["R/C", "RC", "1/RC", "R + C"], "answer": "RC", "why": "The time constant is τ = R × C."},
        {"q": "Which law relates current, voltage and resistance?", "options": ["Faraday's law", "Ohm's law", "Gauss's law", "Coulomb's law"], "answer": "Ohm's law", "why": "Ohm's law states V = IR for an ohmic conductor under constant physical conditions."},
        {"q": "The SI unit of electric charge is:", "options": ["Ampere", "Coulomb", "Watt", "Tesla"], "answer": "Coulomb", "why": "Electric charge is measured in coulombs (C)."},
        {"q": "For a capacitor, charge is given by:", "options": ["Q = CV", "Q = C/V", "Q = V/C", "Q = IR"], "answer": "Q = CV", "why": "The relation between charge, capacitance and potential difference is Q = CV."}
    ],
    "Chemistry": [
        {"q": "The pH of a neutral solution at 25°C is:", "options": ["0", "7", "10", "14"], "answer": "7", "why": "At 25°C, a neutral aqueous solution has pH 7."},
        {"q": "The oxidation state of oxygen in most compounds is:", "options": ["+1", "-1", "-2", "+2"], "answer": "-2", "why": "Oxygen commonly has oxidation state −2, with exceptions such as peroxides."},
        {"q": "Which is the unit of molarity?", "options": ["mol kg⁻¹", "mol L⁻¹", "g L⁻¹", "kg mol⁻¹"], "answer": "mol L⁻¹", "why": "Molarity is moles of solute per litre of solution."},
        {"q": "A catalyst changes the:", "options": ["Equilibrium constant", "Activation energy", "Enthalpy change", "Products"], "answer": "Activation energy", "why": "A catalyst provides an alternative pathway with lower activation energy."},
        {"q": "Which bond involves sharing of electron pairs?", "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "answer": "Covalent", "why": "Covalent bonds form when atoms share electron pairs."}
    ],
    "Mathematics": [
        {"q": "The derivative of x² is:", "options": ["x", "2x", "x³", "2"], "answer": "2x", "why": "Using the power rule, d(xⁿ)/dx = nxⁿ⁻¹."},
        {"q": "The value of sin²θ + cos²θ is:", "options": ["0", "1", "2", "tan θ"], "answer": "1", "why": "This is the fundamental Pythagorean trigonometric identity."},
        {"q": "The determinant of an identity matrix of order 2 is:", "options": ["0", "1", "2", "4"], "answer": "1", "why": "The determinant of every identity matrix is 1."},
        {"q": "The integral of 1/x is:", "options": ["x²/2 + C", "ln|x| + C", "eˣ + C", "1/x² + C"], "answer": "ln|x| + C", "why": "The antiderivative of 1/x is ln|x| + C."},
        {"q": "If two events are independent, then P(A ∩ B) equals:", "options": ["P(A)+P(B)", "P(A)P(B)", "P(A)/P(B)", "0"], "answer": "P(A)P(B)", "why": "For independent events, the probability of both is the product of their probabilities."}
    ],
    "Biology": [
        {"q": "Which organelle is known as the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondrion", "Golgi body"], "answer": "Mitochondrion", "why": "Mitochondria produce most ATP during aerobic respiration."},
        {"q": "DNA stands for:", "options": ["Deoxyribonucleic acid", "Ribonuclear acid", "Dinucleic acid", "Deoxyribose nitrogen acid"], "answer": "Deoxyribonucleic acid", "why": "DNA is deoxyribonucleic acid."},
        {"q": "The functional unit of the kidney is:", "options": ["Neuron", "Nephron", "Alveolus", "Villus"], "answer": "Nephron", "why": "Nephrons filter blood and help form urine."},
        {"q": "Which blood cells help in clotting?", "options": ["Red blood cells", "White blood cells", "Platelets", "Plasma"], "answer": "Platelets", "why": "Platelets help form clots to reduce blood loss."},
        {"q": "Photosynthesis mainly occurs in:", "options": ["Mitochondria", "Chloroplasts", "Nucleus", "Lysosomes"], "answer": "Chloroplasts", "why": "Chloroplasts contain chlorophyll and host photosynthesis."}
    ],
    "Computer Science": [
        {"q": "Which Python data type stores key-value pairs?", "options": ["List", "Tuple", "Dictionary", "Set"], "answer": "Dictionary", "why": "A Python dictionary maps keys to values."},
        {"q": "Which keyword defines a function in Python?", "options": ["func", "define", "def", "function"], "answer": "def", "why": "Python functions are declared using def."},
        {"q": "Which SQL command retrieves data?", "options": ["GET", "SELECT", "FETCHALL", "OPEN"], "answer": "SELECT", "why": "SELECT retrieves rows from database tables."},
        {"q": "Which structure follows FIFO?", "options": ["Stack", "Queue", "Tree", "Graph"], "answer": "Queue", "why": "A queue follows first-in, first-out order."},
        {"q": "What does CSV stand for?", "options": ["Computer Saved Values", "Comma-Separated Values", "Column Stored Variable", "Common System Version"], "answer": "Comma-Separated Values", "why": "CSV is a plain-text tabular data format."}
    ]
}

SUBJECTS = list(QUESTION_BANK.keys())

with st.sidebar:
    st.title("📚 Study Buddy")
    st.caption("Your Class 12 learning companion")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🧠 Take a Quiz", "📅 Study Planner", "📝 My Notes", "📈 Progress"]
    )
    st.divider()
    student_name = st.text_input("Student name", value=st.session_state.get("student_name", "Student"))
    st.session_state.student_name = student_name
    st.caption("Built with Python + Streamlit")

if page == "🏠 Dashboard":
    st.markdown(f"""
    <div class="hero">
      <h1>Welcome, {student_name or 'Student'}! 👋</h1>
      <p>Learn a little every day. Your next step starts here.</p>
    </div>
    """, unsafe_allow_html=True)

    records = st.session_state.progress
    total_quizzes = len(records)
    avg_score = sum(r["percentage"] for r in records) / total_quizzes if total_quizzes else 0
    best_score = max((r["percentage"] for r in records), default=0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Quizzes completed", total_quizzes)
    c2.metric("Average score", f"{avg_score:.1f}%")
    c3.metric("Personal best", f"{best_score:.1f}%")

    st.subheader("🚀 Quick start")
    a, b, c = st.columns(3)
    with a:
        st.info("**Practice**\n\nTest your understanding with subject-wise MCQs.")
    with b:
        st.info("**Plan**\n\nOrganise your study sessions for the week.")
    with c:
        st.info("**Track**\n\nReview your quiz results and progress.")

    st.subheader("📚 Choose a subject")
    cols = st.columns(len(SUBJECTS))
    for col, subject in zip(cols, SUBJECTS):
        with col:
            st.markdown(f"**{subject}**")
            st.caption(f"{len(QUESTION_BANK[subject])} sample questions")

    st.caption("Quiz questions are sample revision questions. Check your school syllabus and textbook for complete preparation.")

elif page == "🧠 Take a Quiz":
    st.title("🧠 Subject Quiz")
    subject = st.selectbox("Choose your subject", SUBJECTS)
    questions = QUESTION_BANK[subject]
    st.write(f"Answer the {len(questions)} questions below.")

    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['q']}**")
            answers[str(i)] = st.radio(
                "Choose one answer",
                q["options"],
                key=f"{subject}_{i}",
                index=None,
                label_visibility="collapsed"
            )
        submitted = st.form_submit_button("Submit quiz", type="primary")

    if submitted:
        unanswered = [i for i, value in answers.items() if value is None]
        if unanswered:
            st.warning("Please answer every question before submitting.")
        else:
            correct = sum(answers[str(i)] == q["answer"] for i, q in enumerate(questions))
            percentage = correct / len(questions) * 100
            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "subject": subject,
                "score": correct,
                "total": len(questions),
                "percentage": round(percentage, 1)
            }
            st.session_state.progress.append(record)
            save_progress(st.session_state.progress)
            st.session_state.last_quiz = {
                "subject": subject, "answers": answers, "correct": correct,
                "percentage": percentage, "questions": questions
            }

    if "last_quiz" in st.session_state and st.session_state.last_quiz["subject"] == subject:
        result = st.session_state.last_quiz
        st.divider()
        st.subheader("Your result")
        st.metric("Score", f"{result['correct']} / {len(result['questions'])}", f"{result['percentage']:.0f}%")
        if result["percentage"] >= 80:
            st.success("Excellent work! Keep it up.")
        elif result["percentage"] >= 50:
            st.info("Good effort. Review the explanations and try again.")
        else:
            st.warning("Keep practising. Learning improves step by step.")
        for i, q in enumerate(result["questions"]):
            chosen = result["answers"][str(i)]
            if chosen == q["answer"]:
                st.success(f"Q{i+1}: Correct — {q['answer']}")
            else:
                st.error(f"Q{i+1}: Your answer: {chosen} | Correct answer: {q['answer']}")
            st.caption(q["why"])

elif page == "📅 Study Planner":
    st.title("📅 Weekly Study Planner")
    st.write("Create a simple plan for your upcoming study sessions.")
    with st.form("planner_form"):
        study_date = st.date_input("Study date", value=date.today())
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic to study", placeholder="e.g. Electrostatics")
        duration = st.number_input("Duration (minutes)", min_value=10, max_value=300, value=45, step=5)
        priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")
        add = st.form_submit_button("Add study task", type="primary")
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if add:
        if topic.strip():
            st.session_state.tasks.append({
                "Date": str(study_date), "Subject": subject,
                "Topic": topic.strip(), "Duration (min)": duration,
                "Priority": priority, "Done": False
            })
            st.success("Study task added.")
        else:
            st.warning("Please enter a topic.")
    if st.session_state.tasks:
        st.subheader("Your tasks")
        for i, task in enumerate(st.session_state.tasks):
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**{task['Subject']} — {task['Topic']}**")
            cols[0].caption(f"{task['Date']} · {task['Duration (min)']} min · {task['Priority']} priority")
            done = cols[1].checkbox("Done", value=task["Done"], key=f"task_{i}")
            st.session_state.tasks[i]["Done"] = done
            if cols[2].button("Delete", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
        completed = sum(t["Done"] for t in st.session_state.tasks)
        st.progress(completed / len(st.session_state.tasks))
        st.caption(f"{completed} of {len(st.session_state.tasks)} tasks completed")
        task_df = pd.DataFrame(st.session_state.tasks)
        st.download_button("Download study plan (CSV)", task_df.to_csv(index=False), "study_plan.csv", "text/csv")
    else:
        st.info("No tasks yet. Add your first study task above.")

elif page == "📝 My Notes":
    st.title("📝 Notes Creator")
    st.write("Write revision notes and download them for later.")
    note_title = st.text_input("Note title", "My Class 12 Revision Notes")
    subject = st.selectbox("Subject", SUBJECTS, key="notes_subject")
    note_body = st.text_area("Write your notes here", height=280, placeholder="Write definitions, formulas, key concepts and examples...")
    st.download_button(
        "⬇️ Download notes as TXT",
        data=f"{note_title}\nSubject: {subject}\nDate: {date.today()}\n\n{note_body}",
        file_name="revision_notes.txt",
        mime="text/plain",
        disabled=not note_body.strip()
    )
    st.download_button(
        "⬇️ Download notes as Markdown",
        data=f"# {note_title}\n\n**Subject:** {subject}  \n**Date:** {date.today()}\n\n{note_body}",
        file_name="revision_notes.md",
        mime="text/markdown",
        disabled=not note_body.strip()
    )

elif page == "📈 Progress":
    st.title("📈 Your Learning Progress")
    records = st.session_state.progress
    if not records:
        st.info("Complete a quiz to see your progress here.")
    else:
        df = pd.DataFrame(records)
        avg = df["percentage"].mean()
        c1, c2, c3 = st.columns(3)
        c1.metric("Quizzes", len(df))
        c2.metric("Average score", f"{avg:.1f}%")
        c3.metric("Best score", f"{df['percentage'].max():.1f}%")

        fig = px.line(
            df.reset_index(), x="index", y="percentage", color="subject",
            markers=True, title="Quiz score history",
            labels={"index": "Quiz number", "percentage": "Score (%)", "subject": "Subject"}
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        subject_avg = df.groupby("subject", as_index=False)["percentage"].mean()
        fig2 = px.bar(subject_avg, x="subject", y="percentage",
                      title="Average score by subject", text_auto=".1f",
                      labels={"subject": "Subject", "percentage": "Average score (%)"})
        fig2.update_yaxes(range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Quiz history")
        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
        st.download_button("Download progress CSV", df.to_csv(index=False), "quiz_progress.csv", "text/csv")
        if st.button("Clear quiz history", type="secondary"):
            st.session_state.progress = []
            save_progress([])
            if "last_quiz" in st.session_state:
                del st.session_state.last_quiz
            st.rerun()

st.divider()
st.caption("AI Study Buddy · Class 12 Capstone Project · Built using Streamlit. This version uses sample questions and local session/data storage; it does not connect to an AI model.")





pip install -r requirements.txt
streamlit run app.py
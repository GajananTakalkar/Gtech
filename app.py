from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

# ============================================
# STORAGE (LOCAL + RENDER FRIENDLY)
# ============================================

# Render gives write-access only to /tmp
if os.environ.get("RENDER"):
    DATA_FOLDER = "/tmp/data"
else:
    DATA_FOLDER = "data"

os.makedirs(DATA_FOLDER, exist_ok=True)

CSV_FILE = os.path.join(DATA_FOLDER, "reg.csv")


# ============================================
# CSV HELPERS
# ============================================

def ensure_csv_exists():
    """Create CSV with header if not found."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Name", "Email", "Course"])
        df.to_csv(CSV_FILE, index=False)
        print("CSV CREATED AT:", CSV_FILE)


def read_csv_safe():
    """Read CSV safely and return empty structure if corrupted."""
    try:
        return pd.read_csv(CSV_FILE)
    except:
        return pd.DataFrame(columns=["Name", "Email", "Course"])


def save_csv(df):
    """Safe write CSV."""
    try:
        df.to_csv(CSV_FILE, index=False)
        print("CSV UPDATED:", CSV_FILE)
    except Exception as e:
        print("CSV WRITE ERROR:", e)


# Create CSV on server start
ensure_csv_exists()


# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/plc_scada')
def plc_scada():
    return render_template("plc_scada.html")


@app.route('/hmi_vfd')
def hmi_vfd():
    return render_template("hmi_vfd.html")


@app.route('/training')
def training():
    return render_template("training.html")


@app.route('/course')
def course():
    return render_template("course.html")


# ============================================
# REGISTRATION FORM
# ============================================

@app.route('/register', methods=["GET", "POST"])
def register():
    courses = ["PLC Basics", "SCADA", "HMI", "Python"]

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        course = request.form.get("course")

        df_old = read_csv_safe()

        new_row = pd.DataFrame([{
            "Name": name,
            "Email": email,
            "Course": course
        }])

        df_all = pd.concat([df_old, new_row], ignore_index=True)
        save_csv(df_all)

        return f"<h2>Thank you, {name}! Your registration for {course} has been saved.</h2>"

    return render_template("register.html", courses=courses)


# ============================================
# DOWNLOAD CSV
# ============================================

@app.route('/download-csv')
def download_csv():
    if not os.path.exists(CSV_FILE):
        return "<h3>No registration data available.</h3>"

    return send_file(
        CSV_FILE,
        download_name="reg.csv",
        as_attachment=True
    )


# ============================================
# VIEW CSV DATA
# ============================================

@app.route('/view-data')
def view_data():
    df = read_csv_safe()

    if df.empty:
        return "<h3>No registration data found.</h3>"

    return df.to_html(classes="table table-striped", justify="center")


# ============================================
# PLC QUIZ
# ============================================

quiz_questions = [
    {
        "question": "What does PLC stand for?",
        "options": ["Programmable Logic Controller", "Power Line Communication",
                    "Programmable Linear Control", "Process Logic Control"],
        "answer": "Programmable Logic Controller"
    },
    {
        "question": "Which language is commonly used to program PLCs?",
        "options": ["C++", "Python", "Ladder Logic", "Assembly"],
        "answer": "Ladder Logic"
    },
    {
        "question": "What is the full scan cycle of a PLC?",
        "options": ["Input -> Execute Program -> Output", "Output -> Input -> Execute",
                    "Scan -> Sleep -> Write", "Input -> Output -> Execute"],
        "answer": "Input -> Execute Program -> Output"
    },
    {
        "question": "Which is a PLC manufacturer?",
        "options": ["Allen-Bradley", "Nokia", "Samsung", "Lenovo"],
        "answer": "Allen-Bradley"
    },
    {
        "question": "What is a rung in Ladder Logic?",
        "options": ["A voltage level", "A row of logic instructions",
                    "A programming error", "An analog signal"],
        "answer": "A row of logic instructions"
    }
]


@app.route('/plc-quiz')
def plc_quiz():
    return render_template("quiz.html", questions=quiz_questions)


@app.route('/plc-quiz/submit', methods=['POST'])
def plc_submit():
    score = 0
    for i, q in enumerate(quiz_questions):
        user_answer = request.form.get(f"q{i}")
        if user_answer == q["answer"]:
            score += 1

    return render_template("result.html", score=score, total=len(quiz_questions))


# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    app.run(debug=True)

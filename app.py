from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import io

app = Flask(__name__)

# ==========================
# RENDER-SAFE STORAGE
# ==========================

if os.environ.get("RENDER"):
    DATA_FOLDER = "/tmp/data"
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # copy initial excel if exists in repo
    if not os.path.exists(os.path.join(DATA_FOLDER, "registration_data.xlsx")):
        if os.path.exists("data/registration_data.xlsx"):
            os.system("cp data/registration_data.xlsx /tmp/data/registration_data.xlsx")
else:
    DATA_FOLDER = "data"
    os.makedirs(DATA_FOLDER, exist_ok=True)

EXCEL_FILE = os.path.join(DATA_FOLDER, "registration_data.xlsx")


# ==========================
# SAFE READ / SAVE
# ==========================

def read_excel_safe(path):
    try:
        return pd.read_excel(path)
    except:
        return pd.DataFrame(columns=["Name", "Email", "Course"])


def save_excel(df, path):
    try:
        df.to_excel(path, index=False)
    except Exception as e:
        print("Excel Write Error:", e)


# ==========================
# ROUTES
# ==========================

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


# ==========================
# REGISTRATION
# ==========================

@app.route('/register', methods=["GET", "POST"])
def register():
    courses = ["PLC Basics", "SCADA", "HMI", "Python"]

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        df_old = read_excel_safe(EXCEL_FILE)

        new_row = pd.DataFrame([{
            "Name": name,
            "Email": email,
            "Course": course
        }])

        df_all = pd.concat([df_old, new_row], ignore_index=True)
        save_excel(df_all, EXCEL_FILE)

        return f"<h2>Thank you, {name}! Your registration for {course} has been saved.</h2>"

    return render_template("register.html", courses=courses)


# ==========================
# DOWNLOAD REGISTRATION FILE
# ==========================

@app.route('/download-excel')
def download_excel():
    if not os.path.exists(EXCEL_FILE):
        return "<h3>No data file found.</h3>"

    return send_file(
        EXCEL_FILE,
        download_name="registration_data.xlsx",
        as_attachment=True
    )


# ==========================
# VIEW REGISTRATION DATA
# ==========================

@app.route('/view-data')
def view_data():
    df = read_excel_safe(EXCEL_FILE)
    if df.empty:
        return "<h3>No registration data found.</h3>"
    return df.to_html()


# ==========================
# PLC QUIZ
# ==========================

quiz_questions = [
    {
        "question": "What does PLC stand for?",
        "options": ["Programmable Logic Controller", "Power Line Communication", "Programmable Linear Control", "Process Logic Control"],
        "answer": "Programmable Logic Controller"
    },
    {
        "question": "Which language is most commonly used to program PLCs?",
        "options": ["C++", "Python", "Ladder Logic", "Assembly"],
        "answer": "Ladder Logic"
    },
    {
        "question": "What is the full scan cycle of a PLC?",
        "options": ["Input -> Execute Program -> Output", "Output -> Input -> Execute", "Scan -> Sleep -> Write", "Input -> Output -> Execute"],
        "answer": "Input -> Execute Program -> Output"
    },
    {
        "question": "Which of these is a PLC manufacturer?",
        "options": ["Allen-Bradley", "Nokia", "Samsung", "Lenovo"],
        "answer": "Allen-Bradley"
    },
    {
        "question": "What is a rung in Ladder Logic?",
        "options": ["A voltage level", "A row of logic instructions", "A programming error", "An analog signal"],
        "answer": "A row of logic instructions"
    }
]

@app.route('/plc-quiz')
def plc_quiz():
    return render_template('quiz.html', questions=quiz_questions)


@app.route('/plc-quiz/submit', methods=['POST'])
def plc_submit():
    score = 0
    for i, q in enumerate(quiz_questions):
        user_answer = request.form.get(f'q{i}')
        if user_answer == q['answer']:
            score += 1
    return render_template('result.html', score=score, total=len(quiz_questions))


# ==========================
# RUN
# ==========================

if __name__ == '__main__':
    app.run(debug=True)

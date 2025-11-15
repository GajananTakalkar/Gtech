from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Writable Excel file path (Render allows writing inside project folders)
EXCEL_FILE = os.path.join("data", "registration_data.xlsx")

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
    return render_template('plc_scada.html')

@app.route('/hmi_vfd')
def hmi_vfd():
    return render_template('hmi_vfd.html')

@app.route('/training')
def training():
    return render_template('training.html')

@app.route('/course')
def course():
    return render_template('course.html')

# ==========================
# REGISTRATION + EXCEL SAVE
# ==========================

@app.route('/register', methods=["GET", "POST"])
def register():
    courses = ["PLC Basics", "SCADA", "HMI", "Python"]

    # Ensure data folder exists
    if not os.path.exists("data"):
        os.makedirs("data")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        new_data = {
            "Name": name,
            "Email": email,
            "Course": course
        }

        # Save to Excel
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            df = pd.DataFrame([new_data])

        df.to_excel(EXCEL_FILE, index=False)

        return f"<h2>Thank you, {name}! Your registration for {course} is saved.</h2>"

    return render_template("register.html", courses=courses)

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
    app.run(debug=True, host='0.0.0.0', port=5000)

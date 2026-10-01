import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "skillpath-demo-secret-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "skillpath_ai.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        location TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS student_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        education TEXT,
        age INTEGER,
        gender TEXT,
        interests TEXT,
        skills TEXT,
        technical_score REAL DEFAULT 0,
        problem_solving_score REAL DEFAULT 0,
        hands_on_score REAL DEFAULT 0,
        communication_score REAL DEFAULT 0,
        digital_score REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS careers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_name TEXT NOT NULL,
        sector TEXT,
        description TEXT,
        education_required TEXT,
        training_duration TEXT,
        nsqf_level TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS career_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        importance INTEGER DEFAULT 1,
        FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_id INTEGER,
        company_name TEXT,
        job_title TEXT,
        location TEXT,
        minimum_salary REAL,
        maximum_salary REAL,
        experience_required TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_id INTEGER NOT NULL,
        experience_years INTEGER,
        minimum_salary REAL,
        maximum_salary REAL,
        FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS training_centres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        centre_name TEXT,
        location TEXT,
        course_name TEXT,
        duration TEXT,
        contact TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        career_id INTEGER NOT NULL,
        match_score REAL,
        reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS family_concerns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        concern_type TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    career_count = cur.execute("SELECT COUNT(*) AS c FROM careers").fetchone()[0]
    if career_count == 0:
        careers = [
            ("Automobile Technician", "Automotive", "Diagnose, service and repair vehicles and mechanical systems.", "ITI / Diploma / vocational training", "6-12 months", "NSQF 4-5"),
            ("Electrician", "Electrical", "Install, maintain and troubleshoot electrical systems.", "ITI / vocational training", "6-12 months", "NSQF 4-5"),
            ("EV Technician", "Electric Mobility", "Service electric vehicles, batteries, motors and charging systems.", "ITI / Diploma / EV training", "6-12 months", "NSQF 4-5"),
            ("Solar Technician", "Renewable Energy", "Install and maintain solar PV systems and related equipment.", "ITI / vocational training", "3-6 months", "NSQF 4"),
            ("Electronics Technician", "Electronics", "Test, repair and maintain electronic devices and systems.", "ITI / Diploma", "6-12 months", "NSQF 4-5"),
            ("CNC Operator", "Manufacturing", "Operate CNC machines and support precision manufacturing.", "ITI / Diploma", "6-12 months", "NSQF 4-5"),
            ("Welder", "Manufacturing", "Perform welding and fabrication work across industrial applications.", "ITI / vocational training", "3-6 months", "NSQF 3-4"),
            ("Healthcare Assistant", "Healthcare", "Support patients and healthcare teams with routine care tasks.", "Healthcare vocational training", "3-6 months", "NSQF 4"),
        ]
        cur.executemany("INSERT INTO careers(career_name,sector,description,education_required,training_duration,nsqf_level) VALUES(?,?,?,?,?,?)", careers)

        skill_map = {
            "Automobile Technician": [("Hands-on repair", 5), ("Diagnostics", 5), ("Mechanical", 4), ("Problem solving", 4)],
            "Electrician": [("Electrical wiring", 5), ("Safety", 5), ("Troubleshooting", 4), ("Hands-on", 4)],
            "EV Technician": [("EV systems", 5), ("Battery technology", 5), ("Electronics", 4), ("Diagnostics", 4)],
            "Solar Technician": [("Solar PV", 5), ("Electrical", 4), ("Installation", 5), ("Safety", 4)],
            "Electronics Technician": [("Electronics", 5), ("Testing", 4), ("Digital skills", 4), ("Troubleshooting", 5)],
            "CNC Operator": [("CNC operation", 5), ("Measurement", 4), ("CAD/CAM basics", 4), ("Precision", 5)],
            "Welder": [("Welding", 5), ("Fabrication", 5), ("Safety", 4), ("Hands-on", 5)],
            "Healthcare Assistant": [("Patient care", 5), ("Communication", 5), ("First aid", 4), ("Empathy", 5)],
        }
        for name, skills in skill_map.items():
            cid = cur.execute("SELECT id FROM careers WHERE career_name=?", (name,)).fetchone()[0]
            cur.executemany("INSERT INTO career_skills(career_id,skill_name,importance) VALUES(?,?,?)", [(cid, s, i) for s, i in skills])

        job_data = [
            ("Tata Motors", "Automobile Technician", "Pune, Maharashtra", 180000, 360000, "0-2 years"),
            ("Maruti Suzuki", "Automobile Technician", "Gurugram, Haryana", 180000, 380000, "0-2 years"),
            ("Larsen & Toubro", "Electrician", "Mumbai, Maharashtra", 180000, 360000, "0-2 years"),
            ("Tata Power", "Electrician", "Delhi NCR", 200000, 420000, "0-2 years"),
            ("Tata Motors EV", "EV Technician", "Pune, Maharashtra", 240000, 500000, "0-2 years"),
            ("Ola Electric", "EV Technician", "Bengaluru, Karnataka", 250000, 550000, "0-2 years"),
            ("Tata Power Solar", "Solar Technician", "Delhi NCR", 180000, 420000, "0-2 years"),
            ("Waaree Energies", "Solar Technician", "Mumbai, Maharashtra", 180000, 400000, "0-2 years"),
            ("Bosch India", "Electronics Technician", "Bengaluru, Karnataka", 220000, 450000, "0-2 years"),
            ("Siemens India", "CNC Operator", "Pune, Maharashtra", 220000, 480000, "0-2 years"),
            ("Bharat Forge", "CNC Operator", "Pune, Maharashtra", 200000, 450000, "0-2 years"),
            ("JSW Steel", "Welder", "Bellary, Karnataka", 180000, 360000, "0-2 years"),
            ("Apollo Hospitals", "Healthcare Assistant", "Delhi NCR", 180000, 330000, "0-2 years"),
        ]
        for company, title, loc, mn, mx, exp in job_data:
            cid = cur.execute("SELECT id FROM careers WHERE career_name=?", (title,)).fetchone()[0]
            cur.execute("INSERT INTO jobs(career_id,company_name,job_title,location,minimum_salary,maximum_salary,experience_required) VALUES(?,?,?,?,?,?,?)", (cid, company, title, loc, mn, mx, exp))

        for name in skill_map:
            cid = cur.execute("SELECT id FROM careers WHERE career_name=?", (name,)).fetchone()[0]
            for years, mn, mx in [(0, 180000, 300000), (2, 300000, 500000), (5, 450000, 750000)]:
                cur.execute("INSERT INTO earnings(career_id,experience_years,minimum_salary,maximum_salary) VALUES(?,?,?,?)", (cid, years, mn, mx))

        centres = [
            ("Industrial Training Institute", "Delhi", "Electrical / Fitter / Electronics", "6-12 months", "Government ITI"),
            ("Skill Development Centre", "Gurugram, Haryana", "Automotive / EV Technician", "6 months", "MSDE / Skill Centre"),
            ("Solar Skill Centre", "Jaipur, Rajasthan", "Solar PV Technician", "3-6 months", "Skill training centre"),
            ("Advanced Manufacturing Centre", "Pune, Maharashtra", "CNC Operator", "6 months", "Skill training centre"),
        ]
        cur.executemany("INSERT INTO training_centres(centre_name,location,course_name,duration,contact) VALUES(?,?,?,?,?)", centres)

    conn.commit()
    conn.close()


def query(sql, params=(), one=False, commit=False):
    conn = get_db()
    try:
        cur = conn.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        rows = cur.fetchone() if one else cur.fetchall()
        return dict(rows) if one and rows else ([dict(r) for r in rows] if rows else [])
    finally:
        conn.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def current_user():
    if "user_id" not in session:
        return None
    return query("SELECT id, name, email, role, location FROM users WHERE id=?", (session["user_id"],), one=True)

CAREER_RULES = {
    "Automobile Technician": {
        "interest": ["automobile", "machines", "mechanical", "cars"],
        "skills": ["hands-on", "problem solving", "technical"],
    },
    "Electrician": {
        "interest": ["electricity", "electronics", "machines", "solar"],
        "skills": ["technical", "problem solving", "hands-on"],
    },
    "EV Technician": {
        "interest": ["automobile", "electronics", "technology", "electricity"],
        "skills": ["technical", "digital", "problem solving"],
    },
    "Solar Technician": {
        "interest": ["solar", "electricity", "electronics", "environment"],
        "skills": ["technical", "hands-on", "problem solving"],
    },
    "Electronics Technician": {
        "interest": ["electronics", "technology", "devices"],
        "skills": ["technical", "digital", "problem solving"],
    },
    "CNC Operator": {
        "interest": ["machines", "manufacturing", "mechanical"],
        "skills": ["technical", "hands-on", "problem solving"],
    },
    "Welder": {
        "interest": ["machines", "construction", "metal", "mechanical"],
        "skills": ["hands-on", "technical"],
    },
    "Healthcare Assistant": {
        "interest": ["healthcare", "people", "medical"],
        "skills": ["communication", "problem solving"],
    },
}


def make_recommendations(profile):
    interests = set(x.strip().lower() for x in (profile.get("interests") or "").split(",") if x.strip())
    skill_scores = {
        "hands-on": float(profile.get("hands_on_score") or 0),
        "technical": float(profile.get("technical_score") or 0),
        "problem solving": float(profile.get("problem_solving_score") or 0),
        "communication": float(profile.get("communication_score") or 0),
        "digital": float(profile.get("digital_score") or 0),
    }

    results = []
    careers = query("SELECT * FROM careers ORDER BY career_name")
    for career in careers:
        rule = CAREER_RULES.get(career["career_name"], {"interest": [], "skills": []})

        interest_hits = len(interests.intersection(set(rule["interest"])))
        interest_score = min(100, interest_hits / max(1, len(rule["interest"])) * 100)

        wanted = rule["skills"] or ["technical"]
        skill_score = sum(skill_scores.get(s, 0) for s in wanted) / len(wanted)

        score = round(0.45 * interest_score + 0.40 * skill_score + 0.15 * 70, 1)

        reasons = []
        if interest_hits:
            reasons.append("Matches your selected interests")
        if skill_score >= 75:
            reasons.append("Fits your aptitude profile")
        if career["training_duration"]:
            reasons.append(f"Training pathway: {career['training_duration']}")
        if not reasons:
            reasons.append("Potential pathway worth exploring")

        results.append({
            "career": career,
            "score": score,
            "reason": " • ".join(reasons)
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


@app.route("/")
def home():
    stats = {
        "careers": query("SELECT COUNT(*) AS c FROM careers", one=True)["c"],
        "jobs": query("SELECT COUNT(*) AS c FROM jobs", one=True)["c"],
        "centres": query("SELECT COUNT(*) AS c FROM training_centres", one=True)["c"],
    }
    return render_template("index.html", stats=stats, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form.get("role", "student")
        location = request.form.get("location", "").strip()

        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return render_template("register.html")

        existing = query("SELECT id FROM users WHERE email=?", (email,), one=True)
        if existing:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        uid = query(
            """INSERT INTO users(name,email,password,role,location)
               VALUES(?,?,?,?,?)""",
            (name, email, generate_password_hash(password), role, location),
            commit=True
        )

        if role == "student":
            query("INSERT INTO student_profiles(user_id) VALUES(?)", (uid,), commit=True)

        session["user_id"] = uid
        flash("Account created successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = query("SELECT * FROM users WHERE email=?", (email,), one=True)

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    profile = query("SELECT * FROM student_profiles WHERE user_id=?", (user["id"],), one=True)

    recommendations = []
    if profile:
        recommendations = make_recommendations(profile)[:3]

    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
        recommendations=recommendations
    )


@app.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    user = current_user()
    if user["role"] != "student":
        flash("The assessment is currently designed for student accounts.", "info")
        return redirect(url_for("dashboard"))

    profile = query("SELECT * FROM student_profiles WHERE user_id=?", (user["id"],), one=True)

    if request.method == "POST":
        education = request.form.get("education", "")
        age = request.form.get("age") or None
        interests = ", ".join(request.form.getlist("interests"))
        scores = {
            "technical_score": int(request.form.get("technical_score", 50)),
            "problem_solving_score": int(request.form.get("problem_solving_score", 50)),
            "hands_on_score": int(request.form.get("hands_on_score", 50)),
            "communication_score": int(request.form.get("communication_score", 50)),
            "digital_score": int(request.form.get("digital_score", 50)),
        }

        query(
            """UPDATE student_profiles
               SET education=?, age=?, interests=?,
                   technical_score=?, problem_solving_score=?,
                   hands_on_score=?, communication_score=?,
                   digital_score=?
               WHERE user_id=?""",
            (
                education, age, interests,
                scores["technical_score"], scores["problem_solving_score"],
                scores["hands_on_score"], scores["communication_score"],
                scores["digital_score"], user["id"]
            ),
            commit=True
        )
        flash("Your career profile has been updated.", "success")
        return redirect(url_for("recommendations"))

    return render_template("assessment.html", profile=profile, user=user)


@app.route("/recommendations")
@login_required
def recommendations():
    user = current_user()
    profile = query("SELECT * FROM student_profiles WHERE user_id=?", (user["id"],), one=True)

    if not profile or not profile.get("education"):
        flash("Complete the assessment first.", "warning")
        return redirect(url_for("assessment"))

    results = make_recommendations(profile)
    for item in results[:5]:
        career = item["career"]
        query(
            """INSERT INTO recommendations(student_id,career_id,match_score,reason)
               VALUES(?,?,?,?)""",
            (user["id"], career["id"], item["score"], item["reason"]),
            commit=True
        )

    return render_template("recommendations.html", results=results, user=user)


@app.route("/careers")
def careers():
    careers = query("SELECT * FROM careers ORDER BY career_name")
    return render_template("careers.html", careers=careers, user=current_user())


@app.route("/career/<int:career_id>")
def career_detail(career_id):
    career = query("SELECT * FROM careers WHERE id=?", (career_id,), one=True)
    if not career:
        return "Career not found", 404

    skills = query(
        "SELECT * FROM career_skills WHERE career_id=? ORDER BY importance DESC",
        (career_id,)
    )
    jobs = query(
        "SELECT * FROM jobs WHERE career_id=? ORDER BY maximum_salary DESC",
        (career_id,)
    )
    earnings = query(
        "SELECT * FROM earnings WHERE career_id=? ORDER BY experience_years",
        (career_id,)
    )

    return render_template(
        "career_detail.html",
        career=career,
        skills=skills,
        jobs=jobs,
        earnings=earnings,
        user=current_user()
    )


@app.route("/compare")
@login_required
def compare():
    ids = request.args.get("ids", "")
    selected = []
    if ids:
        try:
            clean_ids = [int(x) for x in ids.split(",") if x.strip().isdigit()][:3]
            if clean_ids:
                placeholders = ",".join(["?"] * len(clean_ids))
                selected = query(
                    f"SELECT * FROM careers WHERE id IN ({placeholders})",
                    tuple(clean_ids)
                )
        except ValueError:
            pass

    all_careers = query("SELECT id, career_name FROM careers ORDER BY career_name")
    comparison = []
    for career in selected:
        jobs = query(
            "SELECT COUNT(*) AS c, COALESCE(AVG((minimum_salary+maximum_salary)/2),0) AS avg_salary "
            "FROM jobs WHERE career_id=?",
            (career["id"],), one=True
        )
        comparison.append({
            "career": career,
            "job_count": jobs["c"],
            "avg_salary": round(float(jobs["avg_salary"] or 0))
        })

    return render_template(
        "compare.html",
        careers=all_careers,
        comparison=comparison,
        user=current_user()
    )


@app.route("/family")
@login_required
def family():
    user = current_user()
    concerns = query(
        "SELECT * FROM family_concerns WHERE student_id=? ORDER BY created_at DESC",
        (user["id"],)
    )
    return render_template("family.html", user=user, concerns=concerns)


@app.route("/family/concern", methods=["POST"])
@login_required
def add_concern():
    user = current_user()
    concern = request.form.get("concern_type", "Career growth")
    details = request.form.get("description", "")
    query(
        "INSERT INTO family_concerns(student_id,concern_type,description) VALUES(?,?,?)",
        (user["id"], concern, details),
        commit=True
    )
    flash("Family concern saved.", "success")
    return redirect(url_for("family"))


@app.route("/roadmap/<int:career_id>")
@login_required
def roadmap(career_id):
    career = query("SELECT * FROM careers WHERE id=?", (career_id,), one=True)
    if not career:
        return "Career not found", 404
    return render_template("roadmap.html", career=career, user=current_user())


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").lower()

    if "salary" in message or "earning" in message:
        reply = "The platform compares earnings using the demo earnings/job dataset. Open a career page to see salary ranges and progression."
    elif "parent" in message or "family" in message:
        reply = "Use the Family Decision Room to record concerns such as salary, job security, growth, distance, training cost and social perception."
    elif "job" in message:
        reply = "Open Careers and choose a pathway to see associated demo job opportunities and locations."
    elif "recommend" in message or "career" in message:
        reply = "Complete the student assessment. SkillPath AI will calculate an explainable match score from interests and aptitude."
    else:
        reply = "I can help with careers, salary, jobs, training, family concerns and your personalized roadmap."

    return jsonify({"reply": reply})


@app.errorhandler(sqlite3.Error)
def db_error(error):
    return render_template(
        "error.html",
        message="Database error. The local SQLite database could not be read or updated.",
        details=str(error)
    ), 500


# Initialize automatically so Gunicorn/Render also creates the database.
initialize_database()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "skillpath-demo-secret-change-me")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "krish@12"),
    "database": os.getenv("DB_NAME", "skillpath_ai"),
}


def get_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        if getattr(e, "errno", None) != 1049:
            raise
        bootstrap = DB_CONFIG.copy()
        bootstrap.pop("database", None)
        conn = mysql.connector.connect(**bootstrap)
        cur = conn.cursor()
        db_name = DB_CONFIG["database"].replace("`", "")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        conn.commit()
        cur.close()
        conn.close()
        return mysql.connector.connect(**DB_CONFIG)


def initialize_database():
    schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
    seed_path = os.path.join(os.path.dirname(__file__), "database", "seed.sql")
    conn = get_db()
    cur = conn.cursor()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        upper = statement.upper()
        if upper.startswith("CREATE DATABASE") or upper.startswith("USE "):
            continue
        cur.execute(statement)
    conn.commit()
    cur.close()
    conn.close()
    count = query("SELECT COUNT(*) AS c FROM careers", one=True)["c"]
    if count == 0:
        conn = get_db()
        cur = conn.cursor()
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_sql = f.read()
        for statement in seed_sql.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            upper = statement.upper()
            if upper.startswith("USE ") or upper.startswith("DELETE FROM"):
                continue
            cur.execute(statement)
        conn.commit()
        cur.close()
        conn.close()


def query(sql, params=(), one=False, commit=False):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        rows = cur.fetchone() if one else cur.fetchall()
        return rows
    finally:
        cur.close()
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
    return query(
        "SELECT id, name, email, role, location FROM users WHERE id=%s",
        (session["user_id"],),
        one=True
    )


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

        existing = query("SELECT id FROM users WHERE email=%s", (email,), one=True)
        if existing:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        uid = query(
            """INSERT INTO users(name,email,password,role,location)
               VALUES(%s,%s,%s,%s,%s)""",
            (name, email, generate_password_hash(password), role, location),
            commit=True
        )

        if role == "student":
            query("INSERT INTO student_profiles(user_id) VALUES(%s)", (uid,), commit=True)

        session["user_id"] = uid
        flash("Account created successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = query("SELECT * FROM users WHERE email=%s", (email,), one=True)

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
    profile = query("SELECT * FROM student_profiles WHERE user_id=%s", (user["id"],), one=True)

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

    profile = query("SELECT * FROM student_profiles WHERE user_id=%s", (user["id"],), one=True)

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
               SET education=%s, age=%s, interests=%s,
                   technical_score=%s, problem_solving_score=%s,
                   hands_on_score=%s, communication_score=%s,
                   digital_score=%s
               WHERE user_id=%s""",
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
    profile = query("SELECT * FROM student_profiles WHERE user_id=%s", (user["id"],), one=True)

    if not profile or not profile.get("education"):
        flash("Complete the assessment first.", "warning")
        return redirect(url_for("assessment"))

    results = make_recommendations(profile)
    for item in results[:5]:
        career = item["career"]
        query(
            """INSERT INTO recommendations(student_id,career_id,match_score,reason)
               VALUES(%s,%s,%s,%s)""",
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
    career = query("SELECT * FROM careers WHERE id=%s", (career_id,), one=True)
    if not career:
        return "Career not found", 404

    skills = query(
        "SELECT * FROM career_skills WHERE career_id=%s ORDER BY importance DESC",
        (career_id,)
    )
    jobs = query(
        "SELECT * FROM jobs WHERE career_id=%s ORDER BY maximum_salary DESC",
        (career_id,)
    )
    earnings = query(
        "SELECT * FROM earnings WHERE career_id=%s ORDER BY experience_years",
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
                placeholders = ",".join(["%s"] * len(clean_ids))
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
            "FROM jobs WHERE career_id=%s",
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
        "SELECT * FROM family_concerns WHERE student_id=%s ORDER BY created_at DESC",
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
        "INSERT INTO family_concerns(student_id,concern_type,description) VALUES(%s,%s,%s)",
        (user["id"], concern, details),
        commit=True
    )
    flash("Family concern saved.", "success")
    return redirect(url_for("family"))


@app.route("/roadmap/<int:career_id>")
@login_required
def roadmap(career_id):
    career = query("SELECT * FROM careers WHERE id=%s", (career_id,), one=True)
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


@app.errorhandler(Error)
def db_error(error):
    return render_template(
        "error.html",
        message="Database connection/query error. Check your .env settings and MySQL service.",
        details=str(error)
    ), 500


if __name__ == "__main__":
    try:
        initialize_database()
        print("SkillPath AI database initialized successfully.")
    except Exception as e:
        print("Database initialization failed:", e)
    app.run(debug=True, host="127.0.0.1", port=5000)

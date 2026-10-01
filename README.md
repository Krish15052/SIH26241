# SkillPath AI — SIH26241 Full-Stack Prototype

AI-enabled career counselling and family decision-support platform for vocational education.

## Stack
- Python
- Flask
- MySQL
- HTML/CSS/JavaScript
- Bootstrap via local CSS-style prototype (no build system required)

## Setup

1. Create the MySQL database:
   - Open MySQL Workbench.
   - Run `database/schema.sql`.
   - Then run `database/seed.sql`.

2. Create `.env` from `.env.example`:
```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=skillpath_ai
SECRET_KEY=change-this-secret
```

3. Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Install:
```powershell
pip install -r requirements.txt
```

5. Run:
```powershell
python app.py
```

6. Open:
http://127.0.0.1:5000

## Main flow

Home → Register → Student Assessment → AI Recommendations → Career Detail → Family Decision Room → Compare → Roadmap

## Important
The salary/job/training data in `seed.sql` is explicitly demo data for prototyping. Replace it with the official/dataset-provided hackathon data before presenting it as real-world evidence.

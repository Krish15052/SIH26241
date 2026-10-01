CREATE DATABASE IF NOT EXISTS skillpath_ai;
USE skillpath_ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student','parent','counsellor','admin') DEFAULT 'student',
    location VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    education VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    interests TEXT,
    skills TEXT,
    technical_score DECIMAL(5,2) DEFAULT 0,
    problem_solving_score DECIMAL(5,2) DEFAULT 0,
    hands_on_score DECIMAL(5,2) DEFAULT 0,
    communication_score DECIMAL(5,2) DEFAULT 0,
    digital_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS careers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_name VARCHAR(150) NOT NULL,
    sector VARCHAR(100),
    description TEXT,
    education_required VARCHAR(200),
    training_duration VARCHAR(100),
    nsqf_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS career_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT NOT NULL,
    skill_name VARCHAR(150) NOT NULL,
    importance INT DEFAULT 1,
    FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT,
    company_name VARCHAR(200),
    job_title VARCHAR(200),
    location VARCHAR(150),
    minimum_salary DECIMAL(10,2),
    maximum_salary DECIMAL(10,2),
    experience_required VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS earnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT NOT NULL,
    experience_years INT,
    minimum_salary DECIMAL(10,2),
    maximum_salary DECIMAL(10,2),
    FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS training_centres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    centre_name VARCHAR(200),
    location VARCHAR(200),
    course_name VARCHAR(200),
    duration VARCHAR(100),
    contact VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    career_id INT NOT NULL,
    match_score DECIMAL(5,2),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS family_concerns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    concern_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Job Application Tracker Database Schema
-- Run this file to create the database and tables

CREATE DATABASE IF NOT EXISTS job_tracker_test;
USE job_tracker_test;

-- Companies Table
CREATE TABLE IF NOT EXISTS companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
);

-- Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

-- Applications Table
CREATE TABLE IF NOT EXISTS applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT,
    application_date  DATE NOT NULL,
    status            ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn') DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

-- Contacts Table
CREATE TABLE IF NOT EXISTS contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

-- Sample seed data (optional — comment out if not needed)
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp', 'Technology', 'https://techcorp.example.com', 'Austin', 'TX', 'Great culture, remote-friendly'),
('DataCo', 'Data & Analytics', 'https://dataco.example.com', 'San Francisco', 'CA', 'Series B startup'),
('CloudSoft', 'SaaS', 'https://cloudsoft.example.com', 'Seattle', 'WA', NULL);

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, date_posted, requirements) VALUES
(1, 'Software Developer',  'Full-time', 90000, 120000, '2025-01-15', '["Python", "SQL", "Flask"]'),
(2, 'Data Analyst',        'Full-time', 75000, 100000, '2025-01-18', '["Python", "SQL", "Tableau"]'),
(3, 'Backend Engineer',    'Full-time', 100000, 140000, '2025-01-20', '["Python", "Docker", "AWS"]');

INSERT INTO applications (job_id, application_date, status, cover_letter_sent) VALUES
(1, '2025-01-16', 'Interview', TRUE),
(2, '2025-01-19', 'Applied', FALSE),
(3, '2025-01-21', 'Screening', TRUE);

INSERT INTO contacts (company_id, contact_name, title, email, phone) VALUES
(1, 'Jane Smith',    'Engineering Manager',  'jane@techcorp.example.com',  '555-0101'),
(2, 'Bob Johnson',   'Recruiter',            'bob@dataco.example.com',     '555-0202'),
(3, 'Alice Nguyen',  'HR Director',          'alice@cloudsoft.example.com', '555-0303');
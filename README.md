# Job Application Tracker

Its a Flask & MySQL web application for tracking companies, jobs, applications, and contacts in one place.

## Features
- Company management (create, read, update, delete)
- Job management with status and salary tracking (create, read, update, delete)
- Application management with status updates (create, read, update, delete)
- Contact management for recruiter and hiring team details (create, read, update, delete)
- Dashboard metrics for quick progress visibility
- Multi-step wizard flow for faster and easier data input

## Uses
- Python
- Flask
- MySQL
- HTML/CSS

## Quick Start
1. Create database using Schema

2. Install dependencies in requirments:

pip install -r requirements.txt


3. Run the app:

py app.py

4. Open in browser





## Sample data for testing
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

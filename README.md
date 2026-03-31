# Job Application Tracker

A Flask + MySQL web application for tracking companies, jobs, applications, and contacts in one place.

## Features
- Company management (create, read, update, delete)
- Job management with status and salary tracking
- Application management with status updates
- Contact management for recruiter and hiring team details
- Dashboard metrics for quick progress visibility
- Multi-step wizard flow for faster data entry

## Tech Stack
- Python (Flask)
- MySQL
- HTML/CSS

## Quick Start
1. Create database objects:

```bash
mysql -u root -p < schema.sql
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open in browser:

```text
http://127.0.0.1:5000
```
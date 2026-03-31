# AI Usage Documentation

## Tools Used

- **Claude (Anthropic)** — Primary tool used throughout the project for code generation,
  debugging, and architecture decisions.

---

## Key Prompts Used

1. "Help me create this application and the pieces I am missing including the front end
   using the project specification I provided, the database.py and app.py"

2. "Fix the SQL bug in get_applications_by_status — ORDER BY was placed before GROUP BY"

3. "Generate all missing CRUD methods: add_job, add_contact, delete_job, delete_application,
   delete_contact, and all get_*_by_id methods"

4. "Create a complete Flask app.py with routes for all 4 tables including the Job Match feature"

5. "Build the full frontend: base layout with sidebar navigation, dashboard with stats,
   list and form templates for each table, and a job match results page"

6. "Create the database schema SQL file with all 4 tables, foreign keys, and seed data"

---

## What the AI Generated

- **database.py** — Full rewrite with all CRUD methods, dashboard stats query,
  and a dedicated `get_jobs_for_match()` method for the Job Match feature
- **app.py** — All Flask routes for Companies, Jobs, Applications, Contacts,
  Dashboard, and Job Match (POST + GET)
- **schema.sql** — Full CREATE TABLE statements with foreign keys, ENUMs, and
  JSON columns matching the spec; includes optional seed data
- **static/style.css** — Dark-themed UI using CSS variables, sidebar layout,
  stat cards, badge pills for application status, and match result cards
- **All 9 HTML templates** — base.html with sidebar nav, dashboard, list views,
  add/edit forms, and job_match.html with color-coded skill matching results
- **requirements.txt** — Minimal dependency list (Flask, mysql-connector-python)

---

## What I Changed

<!-- Fill in what you personally modified after reviewing the AI output -->

- Updated the MySQL password in `database.py` to match my local setup
- Adjusted the seed data in `schema.sql` to use real companies I am applying to
- Tweaked color values in `style.css` to match my personal preference
- *(Add any other changes you made here)*

---

## What Worked Well

- Claude correctly identified the SQL bug in the original `get_applications_by_status`
  method where `ORDER BY` appeared before `GROUP BY`, which is invalid in MySQL
- The Job Match algorithm accurately computes set intersection between user skills
  and job requirements stored as JSON, then calculates a percentage
- The sidebar navigation with active-state highlighting was generated correctly
  on the first attempt
- Flash messages for create/update/delete feedback worked without modification

---

## What Did Not Work / Needed Fixes

<!-- Document any issues you ran into and how you resolved them -->

- *(e.g. "The edit form for jobs did not pre-populate the date_posted field — I fixed
  the Jinja template to format the date correctly")*
- *(e.g. "Had to update the DB password from 'root' to my actual password")*
- *(Add your own findings here)*

---

## Lessons Learned

- AI is excellent at generating boilerplate CRUD code quickly, but always review
  SQL queries — small bugs like incorrect clause ordering can cause runtime errors
- Providing the AI with the existing code files and the full project spec produced
  much more accurate output than describing requirements from scratch
- AI-generated code often needs variable names, passwords, and placeholder values
  updated to match the actual development environment
- Testing each route manually after generation is important — some edge cases
  (empty form fields, null foreign keys) require extra handling

---

*This project was completed with AI assistance as permitted and encouraged by the
course guidelines. All AI-generated code was reviewed, tested, and adapted by the
student.*
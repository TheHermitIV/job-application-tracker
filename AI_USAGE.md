# AI Usage Documentation

## Tools Used

- **Claude & Copilot** — Are the primary tools used throughout the project for code generation and
  debugging.
- Google


## Key Prompts Used

1. "Help me create this application and the pieces I am missing including the front end with a dark theme using the project specification I provided, the database.py and app.py using flask"

2. "Check for any errors in my CRUD methods"

3. "Create a complete Flask app.py with routes for all 4 tables including the Job Match feature"

4. "Build the full frontend: base layout with sidebar navigation, dashboard with stats, list and form templates for each table, and a job match page"

5. "Check database Schema for errors and create a set of sample data"

6. "Create a wizard for following this format: company, job, application, contact to simplify new applications"

7. "Add input handling and error checks on both client and server side to follow schema constraints"

## What the AI Generated

- **database.py** — Full rewrite of all CRUD methods with server-side validation/error handling, dashboard stats query,
  and a dedicated get_jobs_for_match() method for the Job Match feature
- **app.py** — All Flask routes for Companies, Jobs, Applications, Contacts,
  Dashboard, and Job Match (POST + GET)
- **style.css** — Dark-themed UI, sidebar layout,
  stats, view of application statuses, and match results view
- **HTML templates** — base.html with sidebar nav, dashboard, list views,
  add/edit forms, wizard for easier data input and job_match.html also added Client-side form limits
- **Wizard support** — Multi-step creation flow from company to job to application to contact
- **Sample data** - created sample data which I moved to the read me

## What I Changed

- Changed style.css to fix layout and design to match my personal preference and added a logo
- Reviewed and refined wizard behavior to ensure records are verified after inserts and follows my vision of how it should function
- Tested validation behavior against schema limits (for example length boundaries)
- Adjust Schema
- Made changes to htmls to correct mistakes and to better match match my ideas and improve usability
- Fiexed errors in logic in app and database files

## What Worked Well

- Claude correctly identified the SQL bug in the original Job match feature
- The Job Match algorithm accurately computes set intersection between user skills and job requirements stored as JSON, then calculates a percentage
- The sidebar navigation with active-state highlighting was generated correctly on the first attempts
- Flash messages for create/update/delete feedback worked well
- UI creation was good and only needed a few tweeks
- Logic, input handling, and the general backend was created well
- Wizard feature was implemented the way i wanted to make data inputing much easier without going to multiple pages

## What Did Not Work / Needed Fixes

- **Layout and styling issues** — The generated style.css had layout problems that required me to manualy fixe to match the intended design; several tweaks were needed before the UI looked correct
- **Wizard behavior** — The wizard did not fully follow the steps I wanted it to use after it was generated also needed verification after inserts and just needed to be reviewed and refined
- **Logic errors in app.py and database.py** — Several logic mistakes were present in the generated backend files and had to be manually corrected
- **HTML template mistakes** — Some generated templates contained errors and didnt fit the design which required edits to improve usability
- **SQL bug in Job Match** — The original Job Match feature contained a SQL bug that had to be identified and fixed (Claude caught this on review)
- **input handling** — Form fields required extra validation and handling that wasnt covered at first to match length limits in the schema on the client side
- **File name mismatches** — Some generated files and template references did not match, causing routing or rendering errors that needed to be debugged

## Lessons Learned

- AI was great at generating the backend and adjusting the CRUD code quickly, but always review SQL queries
- Providing the AI with the existing code files and the full project spec made it much more accurate than describing requirements
- AI-generated code often needs variable names, passwords, and placeholder values updated to match the actual development environment
- Testing each route after generation is important and checking file names so they match and work together correctly helped me
catch many issues like the need for extra input handling to make sure everything works as it should
- I also ask copilot to explain any details i dont understand to be able to edit and improve the code it generates
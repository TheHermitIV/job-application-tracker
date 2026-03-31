import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import JobTrackerDB

app = Flask(__name__)
app.secret_key = 'change-me-in-production'


def get_db():
    db = JobTrackerDB()
    db.connect()
    return db


def parse_interview_data(raw_text):
    text = (raw_text or '').strip()
    if not text:
        return None, None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f'Interview data must be valid JSON ({exc.msg}).'
    return json.dumps(parsed), None


def normalize_interview_data_for_form(raw_value):
    if raw_value is None:
        return ''
    if isinstance(raw_value, (dict, list, int, float, bool)):
        return json.dumps(raw_value, indent=2)
    if isinstance(raw_value, (bytes, bytearray)):
        raw_value = raw_value.decode('utf-8', errors='ignore')
    if isinstance(raw_value, str):
        text = raw_value.strip()
        if not text:
            return ''
        try:
            return json.dumps(json.loads(text), indent=2)
        except json.JSONDecodeError:
            return text
    return str(raw_value)


def is_valid_iso_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except (TypeError, ValueError):
        return False


def is_valid_url(url_text):
    """Basic URL validation."""
    if not url_text:
        return True  # Optional field
    url_text = url_text.strip()
    return url_text.startswith(('http://', 'https://'))


def is_valid_email(email_text):
    """Basic email validation."""
    if not email_text:
        return True  # Optional field
    email_text = email_text.strip()
    return '@' in email_text and '.' in email_text.split('@')[1] if '@' in email_text else False


def is_valid_phone(phone_text):
    """Phone validation - allow common formats."""
    if not phone_text:
        return True  # Optional field
    phone_text = phone_text.strip()
    # Allow digits, spaces, hyphens, parentheses, plus
    import re
    return bool(re.match(r'^[\d\s\-\(\)\+]+$', phone_text))


def validate_salary_range(salary_min, salary_max):
    """Validate salary min and max."""
    if not salary_min and not salary_max:
        return True  # Both optional
    if salary_min and salary_max:
        try:
            min_val = int(salary_min)
            max_val = int(salary_max)
            return min_val <= max_val
        except (ValueError, TypeError):
            return False
    return True


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    db = get_db()
    stats = db.get_dashboard_stats()
    db.disconnect()
    return render_template('dashboard.html', stats=stats)


# ─── Companies ────────────────────────────────────────────────────────────────

@app.route('/companies')
def companies():
    db = get_db()
    all_companies = db.get_all_companies()
    db.disconnect()
    return render_template('companies.html', companies=all_companies)


@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        # Validate input lengths to match database schema
        name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        website = request.form.get('website', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        notes = request.form.get('notes', '').strip()
        
        errors = []
        # Validate required field
        if not name:
            errors.append('Company name is required.')
        elif len(name) > 100:
            errors.append('Company name must be 100 characters or less.')
        
        # Validate optional fields
        if len(industry) > 50:
            errors.append('Industry must be 50 characters or less.')
        
        if website:
            if len(website) > 200:
                errors.append('Website must be 200 characters or less.')
            if not is_valid_url(website):
                errors.append('Website must start with http:// or https://.')
        
        if len(city) > 50:
            errors.append('City must be 50 characters or less.')
        if len(state) > 50:
            errors.append('State must be 50 characters or less.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('company_form.html', company=request.form, action='Add')
        
        db = get_db()
        result = db.add_company(
            name=name,
            industry=industry,
            website=website,
            city=city,
            state=state,
            notes=notes,
        )
        db.disconnect()
        if result:
            flash('Company added successfully!', 'success')
            return redirect(url_for('companies'))
        else:
            flash('Failed to add company. Please try again.', 'error')
            return render_template('company_form.html', company=request.form, action='Add')
    return render_template('company_form.html', company=None, action='Add')


@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    db = get_db()
    if request.method == 'POST':
        # Validate input lengths to match database schema
        name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        website = request.form.get('website', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        notes = request.form.get('notes', '').strip()
        
        errors = []
        # Validate required field
        if not name:
            errors.append('Company name is required.')
        elif len(name) > 100:
            errors.append('Company name must be 100 characters or less.')
        
        # Validate optional fields
        if len(industry) > 50:
            errors.append('Industry must be 50 characters or less.')
        
        if website:
            if len(website) > 200:
                errors.append('Website must be 200 characters or less.')
            if not is_valid_url(website):
                errors.append('Website must start with http:// or https://.')
        
        if len(city) > 50:
            errors.append('City must be 50 characters or less.')
        if len(state) > 50:
            errors.append('State must be 50 characters or less.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            company = db.get_company_by_id(company_id)
            db.disconnect()
            return render_template('company_form.html', company=company, action='Edit')
        
        db.update_company_info(
            company_id,
            name=name,
            industry=industry,
            website=website,
            city=city,
            state=state,
            notes=notes,
        )
        db.disconnect()
        flash('Company updated successfully!', 'success')
        return redirect(url_for('companies'))
    company = db.get_company_by_id(company_id)
    db.disconnect()
    return render_template('company_form.html', company=company, action='Edit')


@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    db = get_db()
    db.delete_company(company_id)
    db.disconnect()
    flash('Company deleted.', 'info')
    return redirect(url_for('companies'))


# ─── Jobs ─────────────────────────────────────────────────────────────────────

@app.route('/jobs')
def jobs():
    db = get_db()
    all_jobs = db.get_all_jobs()
    db.disconnect()
    return render_template('jobs.html', jobs=all_jobs)


@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('job_title', '').strip()
        job_url = request.form.get('job_url', '').strip()
        date_posted = request.form.get('date_posted', '').strip()
        salary_min = request.form.get('salary_min', '').strip()
        salary_max = request.form.get('salary_max', '').strip()
        raw_reqs = request.form.get('requirements', '')
        requirements = [s.strip() for s in raw_reqs.split(',') if s.strip()]

        errors = []
        # Validate title
        if not title:
            errors.append('Job title is required.')
        elif len(title) > 100:
            errors.append('Job title must be 100 characters or less.')
        
        # Validate URL
        if job_url and len(job_url) > 300:
            errors.append('Job URL must be 300 characters or less.')
        if job_url and not is_valid_url(job_url):
            errors.append('Job URL must start with http:// or https://.')
        
        # Validate date posted
        if date_posted and not is_valid_iso_date(date_posted):
            errors.append('Date posted must be in YYYY-MM-DD format.')
        
        # Validate salary range
        if not validate_salary_range(salary_min, salary_max):
            errors.append('Salary min must be less than or equal to salary max.')
        
        # Validate salary min
        if salary_min:
            try:
                int(salary_min)
            except ValueError:
                errors.append('Salary min must be a valid number.')
        
        # Validate salary max
        if salary_max:
            try:
                int(salary_max)
            except ValueError:
                errors.append('Salary max must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'error')
            companies = db.get_all_companies()
            db.disconnect()
            return render_template('job_form.html', job=request.form, companies=companies, action='Add')

        db.add_job(
            title=title,
            company_id=request.form.get('company_id') or None,
            job_type=request.form.get('job_type', ''),
            salary_min=salary_min or None,
            salary_max=salary_max or None,
            job_url=job_url,
            date_posted=date_posted or None,
            requirements=requirements,
        )
        db.disconnect()
        flash('Job added successfully!', 'success')
        return redirect(url_for('jobs'))
    companies = db.get_all_companies()
    db.disconnect()
    return render_template('job_form.html', job=None, companies=companies, action='Add')


@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('job_title', '').strip()
        job_url = request.form.get('job_url', '').strip()
        date_posted = request.form.get('date_posted', '').strip()
        salary_min = request.form.get('salary_min', '').strip()
        salary_max = request.form.get('salary_max', '').strip()
        raw_reqs = request.form.get('requirements', '')
        requirements = [s.strip() for s in raw_reqs.split(',') if s.strip()]

        errors = []
        # Validate title
        if not title:
            errors.append('Job title is required.')
        elif len(title) > 100:
            errors.append('Job title must be 100 characters or less.')
        
        # Validate URL
        if job_url and len(job_url) > 300:
            errors.append('Job URL must be 300 characters or less.')
        if job_url and not is_valid_url(job_url):
            errors.append('Job URL must start with http:// or https://.')
        
        # Validate date posted
        if date_posted and not is_valid_iso_date(date_posted):
            errors.append('Date posted must be in YYYY-MM-DD format.')
        
        # Validate salary range
        if not validate_salary_range(salary_min, salary_max):
            errors.append('Salary min must be less than or equal to salary max.')
        
        # Validate salary min
        if salary_min:
            try:
                int(salary_min)
            except ValueError:
                errors.append('Salary min must be a valid number.')
        
        # Validate salary max
        if salary_max:
            try:
                int(salary_max)
            except ValueError:
                errors.append('Salary max must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'error')
            job = db.get_job_by_id(job_id)
            companies = db.get_all_companies()
            db.disconnect()
            return render_template('job_form.html', job=job, companies=companies, action='Edit')

        db.update_job_info(
            job_id,
            title=title,
            company_id=request.form.get('company_id') or None,
            job_type=request.form.get('job_type', ''),
            salary_min=salary_min or None,
            salary_max=salary_max or None,
            job_url=job_url,
            requirements=requirements,
        )
        db.disconnect()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('jobs'))
    job = db.get_job_by_id(job_id)
    companies = db.get_all_companies()
    db.disconnect()
    # Convert requirements JSON to comma-separated string for the form
    if job and job.get('requirements'):
        try:
            reqs = json.loads(job['requirements']) if isinstance(job['requirements'], str) else job['requirements']
            job['requirements_str'] = ', '.join(reqs) if reqs else ''
        except Exception:
            job['requirements_str'] = ''
    return render_template('job_form.html', job=job, companies=companies, action='Edit')


@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    db = get_db()
    db.delete_job(job_id)
    db.disconnect()
    flash('Job deleted.', 'info')
    return redirect(url_for('jobs'))


# ─── Applications ─────────────────────────────────────────────────────────────

@app.route('/applications')
def applications():
    db = get_db()
    status_filter = request.args.get('status', '')
    if status_filter:
        all_apps = db.get_applications_by_status(status_filter)
    else:
        all_apps = db.get_all_applications()
    db.disconnect()
    statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
    return render_template('applications.html', applications=all_apps,
                           statuses=statuses, current_status=status_filter)


@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    db = get_db()
    if request.method == 'POST':
        application_date = request.form.get('application_date', '').strip()
        interview_data, json_error = parse_interview_data(request.form.get('interview_data', ''))

        errors = []
        if not request.form.get('job_id'):
            errors.append('Job is required.')
        if not application_date:
            errors.append('Application date is required.')
        elif not is_valid_iso_date(application_date):
            errors.append('Application date must be in YYYY-MM-DD format.')
        if json_error:
            errors.append(json_error)

        if errors:
            for error in errors:
                flash(error, 'error')
            all_jobs = db.get_all_jobs()
            statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
            db.disconnect()
            return render_template('application_form.html', application=request.form,
                                   jobs=all_jobs, statuses=statuses, action='Add')

        result = db.add_application(
            job_id=request.form.get('job_id'),
            application_date=application_date,
            status=request.form.get('status', 'Applied'),
            resume_version=request.form.get('resume_version', '').strip(),
            cover_letter_sent=bool(request.form.get('cover_letter_sent')),
            interview_data=interview_data,
        )
        db.disconnect()
        if result:
            flash('Application added successfully!', 'success')
            return redirect(url_for('applications'))
        flash('Failed to add application. Please try again.', 'error')
        return redirect(url_for('add_application'))
    all_jobs = db.get_all_jobs()
    db.disconnect()
    statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
    return render_template('application_form.html', application=None,
                           jobs=all_jobs, statuses=statuses, action='Add')


@app.route('/applications/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_application(application_id):
    db = get_db()
    if request.method == 'POST':
        application_date = request.form.get('application_date', '').strip()
        interview_data, json_error = parse_interview_data(request.form.get('interview_data', ''))

        errors = []
        if not request.form.get('job_id'):
            errors.append('Job is required.')
        if not application_date:
            errors.append('Application date is required.')
        elif not is_valid_iso_date(application_date):
            errors.append('Application date must be in YYYY-MM-DD format.')
        if json_error:
            errors.append(json_error)

        if errors:
            for error in errors:
                flash(error, 'error')
            all_jobs = db.get_all_jobs()
            statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
            db.disconnect()
            return render_template('application_form.html', application=request.form,
                                   jobs=all_jobs, statuses=statuses, action='Edit')

        db.update_application_info(
            application_id,
            job_id=request.form.get('job_id'),
            status=request.form.get('status'),
            resume_version=request.form.get('resume_version', '').strip(),
            cover_letter_sent=bool(request.form.get('cover_letter_sent')),
            application_date=application_date,
            interview_data=interview_data,
        )
        db.disconnect()
        flash('Application updated successfully!', 'success')
        return redirect(url_for('applications'))
    application = db.get_application_by_id(application_id)
    if application:
        application['interview_data'] = normalize_interview_data_for_form(application.get('interview_data'))
    all_jobs = db.get_all_jobs()
    db.disconnect()
    statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
    return render_template('application_form.html', application=application,
                           jobs=all_jobs, statuses=statuses, action='Edit')


@app.route('/applications/delete/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    db = get_db()
    db.delete_application(application_id)
    db.disconnect()
    flash('Application deleted.', 'info')
    return redirect(url_for('applications'))


# ─── Contacts ─────────────────────────────────────────────────────────────────

@app.route('/contacts')
def contacts():
    db = get_db()
    all_contacts = db.get_all_contacts()
    db.disconnect()
    return render_template('contacts.html', contacts=all_contacts)


@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('contact_name', '').strip()
        title = request.form.get('title', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        # Validate name
        if not name:
            errors.append('Contact name is required.')
        elif len(name) > 100:
            errors.append('Contact name must be 100 characters or less.')
        
        # Validate title
        if len(title) > 100:
            errors.append('Job title must be 100 characters or less.')
        
        # Validate email
        if email and not is_valid_email(email):
            errors.append('Email must be a valid email address.')
        if email and len(email) > 100:
            errors.append('Email must be 100 characters or less.')
        
        # Validate phone
        if phone and not is_valid_phone(phone):
            errors.append('Phone must contain only digits, spaces, hyphens, parentheses, or plus sign.')
        if phone and len(phone) > 20:
            errors.append('Phone must be 20 characters or less.')
        
        # Validate LinkedIn URL
        if linkedin_url and len(linkedin_url) > 200:
            errors.append('LinkedIn URL must be 200 characters or less.')
        if linkedin_url and not is_valid_url(linkedin_url):
            errors.append('LinkedIn URL must start with http:// or https://.')

        if errors:
            for error in errors:
                flash(error, 'error')
            companies = db.get_all_companies()
            db.disconnect()
            return render_template('contact_form.html', contact=request.form, companies=companies, action='Add')

        db.add_contact(
            company_id=request.form.get('company_id') or None,
            name=name,
            title=title,
            email=email,
            phone=phone,
            linkedin_url=linkedin_url,
            notes=notes,
        )
        db.disconnect()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('contacts'))
    companies = db.get_all_companies()
    db.disconnect()
    return render_template('contact_form.html', contact=None, companies=companies, action='Add')


@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('contact_name', '').strip()
        title = request.form.get('title', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        # Validate name
        if not name:
            errors.append('Contact name is required.')
        elif len(name) > 100:
            errors.append('Contact name must be 100 characters or less.')
        
        # Validate title
        if len(title) > 100:
            errors.append('Job title must be 100 characters or less.')
        
        # Validate email
        if email and not is_valid_email(email):
            errors.append('Email must be a valid email address.')
        if email and len(email) > 100:
            errors.append('Email must be 100 characters or less.')
        
        # Validate phone
        if phone and not is_valid_phone(phone):
            errors.append('Phone must contain only digits, spaces, hyphens, parentheses, or plus sign.')
        if phone and len(phone) > 20:
            errors.append('Phone must be 20 characters or less.')
        
        # Validate LinkedIn URL
        if linkedin_url and len(linkedin_url) > 200:
            errors.append('LinkedIn URL must be 200 characters or less.')
        if linkedin_url and not is_valid_url(linkedin_url):
            errors.append('LinkedIn URL must start with http:// or https://.')

        if errors:
            for error in errors:
                flash(error, 'error')
            contact = db.get_contact_by_id(contact_id)
            companies = db.get_all_companies()
            db.disconnect()
            return render_template('contact_form.html', contact=contact, companies=companies, action='Edit')

        db.update_contact_info(
            contact_id,
            name=name,
            title=title,
            email=email,
            phone=phone,
            company_id=request.form.get('company_id') or None,
            linkedin_url=linkedin_url,
            notes=notes,
        )
        db.disconnect()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('contacts'))
    contact = db.get_contact_by_id(contact_id)
    companies = db.get_all_companies()
    db.disconnect()
    return render_template('contact_form.html', contact=contact, companies=companies, action='Edit')


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    db = get_db()
    db.delete_contact(contact_id)
    db.disconnect()
    flash('Contact deleted.', 'info')
    return redirect(url_for('contacts'))


# ─── Job Match ────────────────────────────────────────────────────────────────

@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    results = []
    user_skills_str = ''
    if request.method == 'POST':
        user_skills_str = request.form.get('skills', '')
        user_skills = {s.strip().lower() for s in user_skills_str.split(',') if s.strip()}

        db = get_db()
        all_jobs = db.get_jobs_for_match()
        db.disconnect()

        for job in all_jobs:
            try:
                reqs_raw = job.get('requirements')
                if reqs_raw:
                    reqs = json.loads(reqs_raw) if isinstance(reqs_raw, str) else reqs_raw
                else:
                    reqs = []
            except (json.JSONDecodeError, TypeError):
                reqs = []

            job_skills = {r.strip().lower() for r in reqs}
            if not job_skills:
                continue

            matched = user_skills & job_skills
            missing = job_skills - user_skills
            pct = round(len(matched) / len(job_skills) * 100)

            results.append({
                'job_title':    job['job_title'],
                'company_name': job.get('company_name', 'Unknown'),
                'salary_min':   job.get('salary_min'),
                'salary_max':   job.get('salary_max'),
                'match_pct':    pct,
                'matched':      sorted(matched),
                'missing':      sorted(missing),
                'total_reqs':   len(job_skills),
            })

        results.sort(key=lambda x: x['match_pct'], reverse=True)

    return render_template('job_match.html', results=results,
                           user_skills=user_skills_str)


# ─── Wizard (Multi-step: Company → Job → Application → Contact) ────────────────

@app.route('/wizard', methods=['GET', 'POST'])
def wizard():
    step = request.form.get('step', request.args.get('step', '1'))
    
    try:
        step = int(step)
    except (ValueError, TypeError):
        step = 1
    
    # Initialize wizard session if needed
    if 'wizard_data' not in session:
        session['wizard_data'] = {}
    
    wizard_data = session['wizard_data']
    
    db = get_db()
    
    # Step 1: Add Company
    if step == 1:
        if request.method == 'POST':
            name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', '').strip()
            website = request.form.get('website', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            notes = request.form.get('notes', '').strip()
            
            errors = []
            if not name:
                errors.append('Company name is required.')
            elif len(name) > 100:
                errors.append('Company name must be 100 characters or less.')
            
            if len(industry) > 50:
                errors.append('Industry must be 50 characters or less.')
            
            if website:
                if len(website) > 200:
                    errors.append('Website must be 200 characters or less.')
                if not is_valid_url(website):
                    errors.append('Website must start with http:// or https://.')
            
            if len(city) > 50:
                errors.append('City must be 50 characters or less.')
            if len(state) > 50:
                errors.append('State must be 50 characters or less.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                db.disconnect()
                return render_template('wizard.html', step=1, wizard_data=wizard_data, 
                                     company_form=request.form)
            
            result = db.add_company(
                name=name,
                industry=industry,
                website=website,
                city=city,
                state=state,
                notes=notes,
            )
            
            if result:
                # Store company_id for next step
                company = db.get_company_by_name(name)
                if company:
                    wizard_data['company_id'] = company['company_id']
                    wizard_data['company_name'] = name
                    session['wizard_data'] = wizard_data
                    db.disconnect()
                    flash('Company added! Now add a job.', 'success')
                    return redirect(url_for('wizard', step=2))
            
            flash('Failed to add company. Please try again.', 'error')
            db.disconnect()
            return render_template('wizard.html', step=1, wizard_data=wizard_data,
                                 company_form=request.form)
        
        db.disconnect()
        return render_template('wizard.html', step=1, wizard_data=wizard_data)
    
    # Step 2: Add Job
    elif step == 2:
        companies = db.get_all_companies()
        
        if request.method == 'POST':
            title = request.form.get('job_title', '').strip()
            job_url = request.form.get('job_url', '').strip()
            date_posted = request.form.get('date_posted', '').strip()
            salary_min = request.form.get('salary_min', '').strip()
            salary_max = request.form.get('salary_max', '').strip()
            raw_reqs = request.form.get('requirements', '')
            requirements = [s.strip() for s in raw_reqs.split(',') if s.strip()]
            
            errors = []
            if not title:
                errors.append('Job title is required.')
            elif len(title) > 100:
                errors.append('Job title must be 100 characters or less.')
            
            if job_url and len(job_url) > 300:
                errors.append('Job URL must be 300 characters or less.')
            if job_url and not is_valid_url(job_url):
                errors.append('Job URL must start with http:// or https://.')
            
            if date_posted and not is_valid_iso_date(date_posted):
                errors.append('Date posted must be in YYYY-MM-DD format.')
            
            if not validate_salary_range(salary_min, salary_max):
                errors.append('Salary min must be less than or equal to salary max.')
            
            if salary_min:
                try:
                    int(salary_min)
                except ValueError:
                    errors.append('Salary min must be a valid number.')
            
            if salary_max:
                try:
                    int(salary_max)
                except ValueError:
                    errors.append('Salary max must be a valid number.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                db.disconnect()
                return render_template('wizard.html', step=2, wizard_data=wizard_data,
                                     companies=companies, job_form=request.form)
            
            # Use company_id from wizard_data if available
            company_id = wizard_data.get('company_id') or request.form.get('company_id') or None
            
            job_id = db.add_job(
                title=title,
                company_id=company_id,
                job_type=request.form.get('job_type', ''),
                salary_min=salary_min or None,
                salary_max=salary_max or None,
                job_url=job_url,
                date_posted=date_posted or None,
                requirements=requirements,
            )
            
            if not job_id:
                flash('Failed to add job. Please check your input and try again.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=2, wizard_data=wizard_data,
                                     companies=companies, job_form=request.form)
            
            # Verify job was created
            job = db.get_job_by_id(job_id)
            if not job:
                flash('Job was added but could not be retrieved. Please try again.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=2, wizard_data=wizard_data,
                                     companies=companies, job_form=request.form)
            
            wizard_data['job_id'] = job_id
            wizard_data['job_title'] = title
            session['wizard_data'] = wizard_data
            
            db.disconnect()
            flash('Job added! Now create an application.', 'success')
            return redirect(url_for('wizard', step=3))
        
        db.disconnect()
        return render_template('wizard.html', step=2, wizard_data=wizard_data,
                             companies=companies)
    
    # Step 3: Add Application
    elif step == 3:
        all_jobs = db.get_all_jobs()
        
        if request.method == 'POST':
            application_date = request.form.get('application_date', '').strip()
            interview_data, json_error = parse_interview_data(request.form.get('interview_data', ''))
            
            errors = []
            if not request.form.get('job_id'):
                errors.append('Job is required.')
            if not application_date:
                errors.append('Application date is required.')
            elif not is_valid_iso_date(application_date):
                errors.append('Application date must be in YYYY-MM-DD format.')
            if json_error:
                errors.append(json_error)
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
                db.disconnect()
                return render_template('wizard.html', step=3, wizard_data=wizard_data,
                                     jobs=all_jobs, statuses=statuses,
                                     application_form=request.form)
            
            job_id = wizard_data.get('job_id') or request.form.get('job_id')
            
            if not job_id:
                flash('Job selection is required.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=3, wizard_data=wizard_data,
                                     jobs=all_jobs, statuses=statuses,
                                     application_form=request.form)
            
            application_id = db.add_application(
                job_id=job_id,
                application_date=application_date,
                status=request.form.get('status', 'Applied'),
                resume_version=request.form.get('resume_version', '').strip(),
                cover_letter_sent=bool(request.form.get('cover_letter_sent')),
                interview_data=interview_data,
            )
            
            if not application_id:
                flash('Failed to create application. Please check your input and try again.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=3, wizard_data=wizard_data,
                                     jobs=all_jobs, statuses=statuses,
                                     application_form=request.form)
            
            # Verify application was created
            application = db.get_application_by_id(application_id)
            if not application:
                flash('Application was created but could not be retrieved. Please try again.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=3, wizard_data=wizard_data,
                                     jobs=all_jobs, statuses=statuses,
                                     application_form=request.form)
            
            wizard_data['application_id'] = application_id
            session['wizard_data'] = wizard_data
            
            db.disconnect()
            flash('Application added! Now add a contact (optional).', 'success')
            return redirect(url_for('wizard', step=4))
        
        statuses = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
        db.disconnect()
        return render_template('wizard.html', step=3, wizard_data=wizard_data,
                             jobs=all_jobs, statuses=statuses)
    
    # Step 4: Add Contact (Optional)
    elif step == 4:
        companies = db.get_all_companies()
        
        if request.method == 'POST':
            # Check if user wants to skip
            if request.form.get('skip_contact'):
                db.disconnect()
                session['wizard_data'] = {}
                session.modified = True
                flash('Wizard complete! Your job application has been saved.', 'success')
                return redirect(url_for('dashboard'))
            
            name = request.form.get('contact_name', '').strip()
            title = request.form.get('title', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            notes = request.form.get('notes', '').strip()
            
            errors = []
            if not name:
                errors.append('Contact name is required.')
            elif len(name) > 100:
                errors.append('Contact name must be 100 characters or less.')
            
            if len(title) > 100:
                errors.append('Job title must be 100 characters or less.')
            
            if email and not is_valid_email(email):
                errors.append('Email must be a valid email address.')
            if email and len(email) > 100:
                errors.append('Email must be 100 characters or less.')
            
            if phone and not is_valid_phone(phone):
                errors.append('Phone must contain only digits, spaces, hyphens, parentheses, or plus sign.')
            if phone and len(phone) > 20:
                errors.append('Phone must be 20 characters or less.')
            
            if linkedin_url and len(linkedin_url) > 200:
                errors.append('LinkedIn URL must be 200 characters or less.')
            if linkedin_url and not is_valid_url(linkedin_url):
                errors.append('LinkedIn URL must start with http:// or https://.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                db.disconnect()
                return render_template('wizard.html', step=4, wizard_data=wizard_data,
                                     companies=companies, contact_form=request.form)
            
            # Try to link to company from wizard if available
            company_id = wizard_data.get('company_id') or request.form.get('company_id') or None
            
            contact_id = db.add_contact(
                company_id=company_id,
                name=name,
                title=title,
                email=email,
                phone=phone,
                linkedin_url=linkedin_url,
                notes=notes,
            )
            
            if not contact_id:
                flash('Failed to add contact. Please check your input and try again.', 'error')
                db.disconnect()
                return render_template('wizard.html', step=4, wizard_data=wizard_data,
                                     companies=companies, contact_form=request.form)
            
            # Verify contact was created
            contact = db.get_contact_by_id(contact_id)
            if not contact:
                flash('Contact was added but could not be retrieved. Completing wizard anyway.', 'warning')
            
            db.disconnect()
            session['wizard_data'] = {}
            session.modified = True
            flash('Wizard complete! Application and contact saved.', 'success')
            return redirect(url_for('dashboard'))
        
        db.disconnect()
        return render_template('wizard.html', step=4, wizard_data=wizard_data,
                             companies=companies)
    
    db.disconnect()
    return redirect(url_for('wizard', step=1))


if __name__ == '__main__':
    app.run(debug=True)
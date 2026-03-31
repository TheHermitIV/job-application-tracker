import mysql.connector
from mysql.connector import Error
import json


_UNSET = object()


class JobTrackerDB:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'job_tracker_test'
        }
        self.connection = None

    # ─── Connection Management ───────────────────────────────────────────────

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            print(f'Connection error: {e}')
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    # ─── Dashboard Stats ──────────────────────────────────────────────────────

    def get_dashboard_stats(self):
        cursor = self.connection.cursor(dictionary=True)
        stats = {}

        cursor.execute('SELECT COUNT(*) AS total FROM applications')
        stats['total_applications'] = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM companies')
        stats['total_companies'] = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM jobs')
        stats['total_jobs'] = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM contacts')
        stats['total_contacts'] = cursor.fetchone()['total']

        cursor.execute(
            'SELECT status, COUNT(*) AS cnt FROM applications GROUP BY status'
        )
        stats['by_status'] = {row['status']: row['cnt'] for row in cursor.fetchall()}

        cursor.execute('''
            SELECT a.application_id, j.job_title, c.company_name,
                   a.application_date, a.status
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
            LIMIT 5
        ''')
        stats['recent_applications'] = cursor.fetchall()
        return stats

    # ─── SELECT Queries ───────────────────────────────────────────────────────

    def get_all_companies(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM companies ORDER BY company_name')
        return cursor.fetchall()

    def get_company_by_id(self, company_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM companies WHERE company_id = %s', (company_id,))
        return cursor.fetchone()

    def get_all_jobs(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT j.job_id, j.job_title, j.job_type, j.salary_min,
                   j.salary_max, j.job_url, j.date_posted, j.requirements,
                   c.company_name, c.company_id
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.date_posted DESC
        ''')
        return cursor.fetchall()

    def get_job_by_id(self, job_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT j.*, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            WHERE j.job_id = %s
        ''', (job_id,))
        return cursor.fetchone()

    def get_all_applications(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.application_id, a.application_date, a.status,
                   a.resume_version, a.cover_letter_sent,
                   j.job_title, c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
        ''')
        return cursor.fetchall()

    def get_application_by_id(self, application_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, j.job_title, c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        ''', (application_id,))
        return cursor.fetchone()

    def get_all_contacts(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT ct.*, c.company_name
            FROM contacts ct
            LEFT JOIN companies c ON ct.company_id = c.company_id
            ORDER BY ct.contact_name
        ''')
        return cursor.fetchall()

    def get_contact_by_id(self, contact_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT ct.*, c.company_name
            FROM contacts ct
            LEFT JOIN companies c ON ct.company_id = c.company_id
            WHERE ct.contact_id = %s
        ''', (contact_id,))
        return cursor.fetchone()

    def get_jobs_by_salary(self, min_salary):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM jobs WHERE salary_min >= %s', (min_salary,))
        return cursor.fetchall()

    def get_applications_by_status(self, status):
        """Fixed: GROUP BY must precede ORDER BY in MySQL."""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.application_id, j.job_title, c.company_name,
                   a.application_date, a.status
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.status = %s
            GROUP BY a.application_id
            ORDER BY a.application_date DESC
        ''', (status,))
        return cursor.fetchall()

    def get_jobs_by_company(self, company_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM jobs WHERE company_id = %s', (company_id,))
        return cursor.fetchall()

    def get_jobs_for_match(self):
        """Return all jobs with their requirements JSON for the Job Match feature."""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT j.job_id, j.job_title, j.salary_min, j.salary_max,
                   j.requirements, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
        ''')
        return cursor.fetchall()

    # ─── INSERT Queries ───────────────────────────────────────────────────────

    def add_company(self, name, industry, website, city, state, notes=''):
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO companies (company_name, industry, website, city, state, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, industry, website, city, state, notes))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f'Error adding company: {e}')
            self.connection.rollback()
            return None

    def add_job(self, title, company_id, job_type, salary_min, salary_max,
                job_url, date_posted, requirements):
        cursor = self.connection.cursor()
        req_json = json.dumps(requirements) if isinstance(requirements, list) else requirements
        try:
            cursor.execute('''
                INSERT INTO jobs
                    (job_title, company_id, job_type, salary_min, salary_max,
                     job_url, date_posted, requirements)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (title, company_id, job_type, salary_min, salary_max,
                  job_url, date_posted, req_json))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f'Error adding job: {e}')
            self.connection.rollback()
            return None

    def add_application(self, job_id, application_date, status='Applied',
                        resume_version='', cover_letter_sent=False,
                        interview_data=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO applications
                    (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (job_id, application_date, status, resume_version, cover_letter_sent, interview_data))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f'Error adding application: {e}')
            self.connection.rollback()
            return None

    def add_contact(self, company_id, name, title, email, phone,
                    linkedin_url='', notes=''):
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO contacts
                    (company_id, contact_name, title, email, phone, linkedin_url, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (company_id or None, name, title, email, phone, linkedin_url, notes))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f'Error adding contact: {e}')
            self.connection.rollback()
            return None

    # ─── UPDATE Queries ───────────────────────────────────────────────────────

    def update_company_info(self, company_id, name=None, industry=None,
                            website=None, city=None, state=None, notes=None):
        cursor = self.connection.cursor()
        fields, values = [], []
        if name     is not None: fields.append('company_name = %s'); values.append(name)
        if industry is not None: fields.append('industry = %s');     values.append(industry)
        if website  is not None: fields.append('website = %s');      values.append(website)
        if city     is not None: fields.append('city = %s');         values.append(city)
        if state    is not None: fields.append('state = %s');        values.append(state)
        if notes    is not None: fields.append('notes = %s');        values.append(notes)
        if not fields:
            return 0
        values.append(company_id)
        cursor.execute(
            f'UPDATE companies SET {", ".join(fields)} WHERE company_id = %s',
            tuple(values)
        )
        self.connection.commit()
        return cursor.rowcount

    def update_job_info(self, job_id, title=None, company_id=None,
                        job_type=None, salary_min=None, salary_max=None,
                        job_url=None, requirements=None):
        cursor = self.connection.cursor()
        fields, values = [], []
        if title       is not None: fields.append('job_title = %s');   values.append(title)
        if company_id  is not None: fields.append('company_id = %s');  values.append(company_id)
        if job_type    is not None: fields.append('job_type = %s');    values.append(job_type)
        if salary_min  is not None: fields.append('salary_min = %s');  values.append(salary_min)
        if salary_max  is not None: fields.append('salary_max = %s');  values.append(salary_max)
        if job_url     is not None: fields.append('job_url = %s');     values.append(job_url)
        if requirements is not None:
            fields.append('requirements = %s')
            values.append(
                json.dumps(requirements) if isinstance(requirements, list) else requirements
            )
        if not fields:
            return 0
        values.append(job_id)
        cursor.execute(
            f'UPDATE jobs SET {", ".join(fields)} WHERE job_id = %s',
            tuple(values)
        )
        self.connection.commit()
        return cursor.rowcount

    def update_application_status(self, application_id, new_status):
        cursor = self.connection.cursor()
        cursor.execute(
            'UPDATE applications SET status = %s WHERE application_id = %s',
            (new_status, application_id)
        )
        self.connection.commit()
        return cursor.rowcount

    def update_application_info(self, application_id, job_id=None, status=None,
                                resume_version=None, cover_letter_sent=None,
                                application_date=None, interview_data=_UNSET):
        cursor = self.connection.cursor()
        fields, values = [], []
        if job_id            is not None: fields.append('job_id = %s');            values.append(job_id)
        if application_date  is not None: fields.append('application_date = %s');  values.append(application_date)
        if status            is not None: fields.append('status = %s');            values.append(status)
        if resume_version    is not None: fields.append('resume_version = %s');    values.append(resume_version)
        if cover_letter_sent is not None: fields.append('cover_letter_sent = %s'); values.append(cover_letter_sent)
        if interview_data is not _UNSET:
            fields.append('interview_data = %s')
            values.append(interview_data)
        if not fields:
            return 0
        values.append(application_id)
        cursor.execute(
            f'UPDATE applications SET {", ".join(fields)} WHERE application_id = %s',
            tuple(values)
        )
        self.connection.commit()
        return cursor.rowcount

    def update_contact_info(self, contact_id, name=None, email=None,
                            phone=None, company_id=None, title=None,
                            linkedin_url=None, notes=None):
        cursor = self.connection.cursor()
        fields, values = [], []
        if name        is not None: fields.append('contact_name = %s'); values.append(name)
        if email       is not None: fields.append('email = %s');        values.append(email)
        if phone       is not None: fields.append('phone = %s');        values.append(phone)
        if company_id  is not None: fields.append('company_id = %s');   values.append(company_id)
        if title       is not None: fields.append('title = %s');        values.append(title)
        if linkedin_url is not None: fields.append('linkedin_url = %s'); values.append(linkedin_url)
        if notes       is not None: fields.append('notes = %s');        values.append(notes)
        if not fields:
            return 0
        values.append(contact_id)
        cursor.execute(
            f'UPDATE contacts SET {", ".join(fields)} WHERE contact_id = %s',
            tuple(values)
        )
        self.connection.commit()
        return cursor.rowcount

    def update_company_notes(self, company_id, notes):
        cursor = self.connection.cursor()
        cursor.execute(
            'UPDATE companies SET notes = %s WHERE company_id = %s',
            (notes, company_id)
        )
        self.connection.commit()
        return cursor.rowcount

    # ─── DELETE Queries ───────────────────────────────────────────────────────

    def delete_company(self, company_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM companies WHERE company_id = %s', (company_id,))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f'Error deleting company: {e}')
            self.connection.rollback()
            return 0

    def delete_job(self, job_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM jobs WHERE job_id = %s', (job_id,))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f'Error deleting job: {e}')
            self.connection.rollback()
            return 0

    def delete_application(self, application_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM applications WHERE application_id = %s', (application_id,))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f'Error deleting application: {e}')
            self.connection.rollback()
            return 0

    def delete_contact(self, contact_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM contacts WHERE contact_id = %s', (contact_id,))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f'Error deleting contact: {e}')
            self.connection.rollback()
            return 0

    # ─── Helper Methods for Wizard ────────────────────────────────────────────

    def get_company_by_name(self, name):
        """Get company by name (used after adding to get the ID)."""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM companies WHERE company_name = %s LIMIT 1', (name,))
            return cursor.fetchone()
        except Error as e:
            print(f'Error fetching company by name: {e}')
            return None

    def get_job_by_title(self, title):
        """Get job by title (used after adding to get the ID)."""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM jobs WHERE job_title = %s ORDER BY job_id DESC LIMIT 1', (title,))
            return cursor.fetchone()
        except Error as e:
            print(f'Error fetching job by title: {e}')
            return None

    def get_application_by_job_and_date(self, job_id, application_date):
        """Get application by job_id and date (used after adding to get the ID)."""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                'SELECT * FROM applications WHERE job_id = %s AND application_date = %s ORDER BY application_id DESC LIMIT 1',
                (job_id, application_date)
            )
            return cursor.fetchone()
        except Error as e:
            print(f'Error fetching application: {e}')
            return None


# ─── Example Usage ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    db = JobTrackerDB()
    if db.connect():
        companies = db.get_all_companies()
        print(f'Found {len(companies)} companies')
        for c in companies:
            print(f"  - {c['company_name']}")
        db.disconnect()
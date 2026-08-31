from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

db_connection_string = os.getenv('DB_CONNECTION_STRING')

engine = create_engine(
    db_connection_string,
    pool_pre_ping=True
)


def load_jobs_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM jobs"))

        jobs = []

        for row in result.all():
            jobs.append(dict(row._mapping))


        return jobs

def load_one_job_from_db(job_id):
    with engine.connect() as conn:
        result = conn.execute(
                    text("SELECT * FROM jobs WHERE job_id = :val"),
                    {"val": job_id}
                )
        job = result.first()


        if job is None:
            return None
        
        return dict(job._mapping)


def add_application_to_db(user_id, job_id, data):
    with engine.connect() as conn:
        query = text(
            """INSERT INTO applications (user_id, job_id, status, applied_on) values (:user_id, :job_id, :status, :applied_on)"""
                    )

        conn.execute(query, {
                    "user_id" : user_id,
                    "job_id" : job_id,
                    "status" : "",
                    "applied_on" : date.today()
                })
        conn.commit()


def add_users_to_db(
    name,
    email,
    password,
    headline="",
    linkedin="",
    education="",
    experience="",
    resume=""
):
    with engine.connect() as conn:
        query = text("""
            INSERT INTO users (
                name,
                email,
                password,
                headline,
                linkedin_url,
                education,
                work_experience,
                resume_url
            )
            VALUES (
                :name,
                :email,
                :password,
                :headline,
                :linkedin_url,
                :education,
                :work_experience,
                :resume_url
            )
        """)

        conn.execute(query, {
            "name": name,
            "email": email,
            "password": password.decode("utf-8"),
            "headline": headline or "",
            "linkedin_url": linkedin or "",
            "education": education or "",
            "work_experience": experience or "",
            "resume_url": resume or "",
        })
        conn.commit()


def get_user_from_db(email):
    with engine.connect() as conn:
        query = text(
            "SELECT * FROM users WHERE email = :email"
        )

        result = conn.execute(query,{
                    "email" : email,
                })
        
        user = result.fetchone()
        if user is None:
            return None

        return dict(user._mapping)
        

def get_user_info_from_db(user_id):
    with engine.connect() as conn:
        query = text(
            "SELECT * FROM users WHERE user_id = :user_id"
        )

        result = conn.execute(query,{
                    "user_id" : user_id
                })
        data = result.fetchone()
        if data is None:
            return None

        return dict(data._mapping)


def get_application_info_from_db(user_id):
    with engine.connect() as conn:
        # Explicitly name the columns instead of using j.* and a.*
        query = text(
            "SELECT j.job_id, j.title, j.company, a.status, a.applied_on "
            "FROM jobs AS j "
            "JOIN applications AS a ON j.job_id = a.job_id "
            "WHERE a.user_id = :user_id"
        )

        result = conn.execute(query, {
            "user_id" : user_id
        })

        # Fetch the results into a variable first
        rows = result.fetchall()

        data = []
        for row in rows:
            data.append(dict(row._mapping))
            
        # Print the result to your terminal so you can debug what is happening
        print(f"DEBUG - Fetched Data for User {user_id}: {data}")

        return data


def had_user_applied(user_id, job_id):
    with engine.connect() as conn:
        query = text(
            "Select 1 from applications where user_id = :user_id and job_id = :job_id limit 1"
        )

        result = conn.execute(query,{
            "user_id" : user_id,
            "job_id" : job_id
        })

        return result.first() is not None


def update_user_profile(user_id, data):
    with engine.connect() as conn:
        query = text("update users " \
        "set name = :name, email = :email, linkedin_url = :linkedin_url," \
        "education = :education, work_experience = :work_experience, resume_url = :resume_url" \
        " where user_id = :user_id")

        conn.execute(query,{
            "user_id" : user_id,
            "name" : data['full_name'],
            "email" : data['email'],
            "linkedin_url" : data['linkedin_url'],
            "education" : data['education'],
            "work_experience" : data['work_experience'],
            "resume_url" : data['resume_url']
        })

        conn.commit()


def search_jobs_from_db(query):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM jobs WHERE title LIKE :q OR company LIKE :q OR location LIKE :q"),
            {"q": f"%{query}%"}
        )

        jobs = []
        for row in result.all():
            jobs.append(dict(row._mapping))

        return jobs


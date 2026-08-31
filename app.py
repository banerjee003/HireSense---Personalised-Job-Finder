from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from database import load_jobs_from_db, load_one_job_from_db, add_application_to_db, add_users_to_db, get_user_from_db, get_user_info_from_db,get_application_info_from_db,had_user_applied,update_user_profile,search_jobs_from_db
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import bcrypt
import os


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('APP_SECRET_KEY')
csrf = CSRFProtect(app)


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

    headline = StringField("Headline")
    linkedin = StringField("Linked in")
    education = StringField("Education")
    experience = StringField("Experience")
    resume = StringField("Resume")
    submit = SubmitField("Register")

    def validate_email(self,field):
        user = get_user_from_db(field.data)
        if user:
            raise ValidationError('Email already taken')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


@app.route('/')
def hello_world():
    jobs = load_jobs_from_db()
    return render_template('index.html', jobs=jobs)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        headline = form.headline.data
        education = form.education.data
        linkedin = form.linkedin.data
        experience = form.experience.data
        resume = form.resume.data


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # form.validate_email(email)

        add_users_to_db(name=name, email=email, password=hashed_password, headline=headline, education=education, 
                        linkedin=linkedin, experience=experience, resume=resume)
        
        user = get_user_from_db(email=email)
        session['user_id'] = user['user_id']
        flash("Registration Successful.")
        return redirect(url_for('hello_world'))


    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = get_user_from_db(email=email)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['user_id']
            return redirect(url_for('hello_world'))
        else:
            flash("Login Failed. Please check your email and password!")

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user_info_from_db(user_id=user_id)

        if user :
            data = get_application_info_from_db(user_id)
            return render_template('dashboard.html',user=user,data=data)

    flash("Please Login")
    return redirect(url_for('login'))


@app.route('/jobs/<job_id>')
def show_job(job_id):
    job = load_one_job_from_db(job_id)

    if not job:
        return 'Not Found', 404

    user = None
    has_applied = False
    if "user_id" in session:
        user = get_user_info_from_db(session["user_id"])
        has_applied = had_user_applied(session["user_id"], job_id)

    return render_template('jobpage.html', job=job, user=user, has_applied=has_applied)


@app.route('/jobs/<job_id>/apply', methods=['post'])
def apply_to_job(job_id):
    user_id = session.get("user_id")

    if user_id is None:
        flash("Please log in before applying.")
        return redirect(url_for("login"))

    data = request.form
    add_application_to_db(user_id,job_id,data)
    flash("Application submitted successfully.")
    return redirect(url_for("show_job", job_id=job_id))


@app.route('/edit', methods=["GET","POST"])
def edit():
    user_id = session.get("user_id")

    if user_id is None:
        flash('Please log in')
        return redirect(url_for("login"))

    if request.method == "POST":
        update_user_profile(user_id=user_id, data=request.form)
        flash("Profile Updated Successfully.")
        return redirect(url_for("dashboard"))

    data = get_user_info_from_db(user_id)

    return render_template('edit_profile.html', user=data)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        jobs = search_jobs_from_db(query)
    else:
        jobs = load_jobs_from_db()
    return render_template('index.html', jobs=jobs, search_query=query)


@app.route("/api/jobs")
def list_jobs():
    jobs = load_jobs_from_db()
    return jsonify(jobs)


if __name__ == '__main__':
    app.run(debug=True)

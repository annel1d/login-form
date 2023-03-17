from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.jobs import JobsForm
from forms.user import RegisterForm, LoginForm
from data.jobs import Jobs
from data.users import User
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/b1logs.db")
    app.run()


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.job = form.title.data
        jobs.team_leader = form.tl_id.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.is_finished = form.is_finished.data
        db_sess.merge(jobs)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление работы', form=form)


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()
        if jobs:
            form.title.data = jobs.title
            form.content.data = jobs.content
            form.is_private.data = jobs.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()
        if Jobs:
            jobs.title = form.title.data
            jobs.content = form.content.data
            jobs.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html', title='Редактирование работы', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        jobs = db_sess.query(Jobs).filter((Jobs.is_finished != True))
    else:
        jobs = db_sess.query(Jobs).filter(Jobs.is_finished != True)
    return render_template("index.html", jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            address=form.address.data,
            speciality=form.speciality.data,
            age=form.age.data,
            position=form.position.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()

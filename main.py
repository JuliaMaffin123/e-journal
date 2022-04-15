from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, current_user, login_user, logout_user, login_fresh
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

from data import db_session
from data.classes import Classes
from data.menu import Menu
from data.role import Role
from data.users import Users

app = Flask('MyApp')
app.config['SECRET_KEY'] = 'brbrbr'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/school.db")
session = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


class LoginForm(FlaskForm):
    identifier = StringField()
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisrationForm(FlaskForm):
    identifier = StringField()
    username = StringField('Логин', validators=[DataRequired(), Length(max=64)])
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Повторите пароль',
        validators=[DataRequired(), Length(min=8)])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    otchestvo = StringField('Отчество')
    submit = SubmitField('Зарегистрироваться')


@app.route('/', methods=['GET', 'POST'])
def login():
    if not login_fresh():
        formL = LoginForm()
        formR = RegisrationForm()
        if formL.identifier.data == 'LOGIN' and formL.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(Users).filter(Users.login == formL.username.data and Users.active == 1).first()
            if user and user.password == formL.password.data:
                if user.role == 'guest':
                    return render_template('page_guest.html', name=user.name, surname=user.surname)
                else:
                    role = db_sess.query(Role).filter(Role.name == user.role).first()
                    login_user(user)
                    return redirect(f"/{role.start_page}")
            return render_template('login_form.html',
                                   message="Неправильный логин или пароль",
                                   formL=formL, formR=formR)
        if formR.identifier.data == 'REGISTRATION' and formR.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(Users).filter(Users.login == formR.username.data).first()
            if user:
                return render_template('login_form.html',
                                       message="Такой логин уже занят",
                                       formL=formL, formR=formR)
            if not formR.password.data == formR.confirm_password.data:
                return render_template('login_form.html',
                                       message="Пароли должны совпадать",
                                       formL=formL, formR=formR)
            newUser = Users(name=formR.name.data,
                            surname=formR.surname.data,
                            otchestvo=formR.otchestvo.data,
                            login=formR.username.data,
                            password=formR.password.data,
                            role="guest",
                            active=1,
                            class_id=1)
            db_sess.add(newUser)
            db_sess.commit()
            return render_template('page_guest.html', name=formR.name.data, surname=formR.surname.data)
        return render_template('login_form.html', formL=formL, formR=formR)
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == current_user.login and Users.active == 1).first()
        role = db_sess.query(Role).filter(Role.name == user.role).first()
        if role == 'guest':
            return render_template('page_guest.html', name=user.name, surname=user.surname)
        else:
            return redirect(f"/{role.start_page}")


@app.route('/logout', methods=['GET'])
def logout():
    print('current_user.name=' + current_user.name)
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('page_error.html',
                           number="404",
                           header="Page not found",
                           description="Извините, но мы не смогли найти эту страницу"), 404


@app.route('/admin/dashboard')
def admin_dashboard():
    db_sess = db_session.create_session()
    class_cnt = db_sess.query(Classes).count()
    teacher_cnt = db_sess.query(Users).filter(Users.role == 'teacher' and Users.active == 1).count()
    student_cnt = db_sess.query(Users).filter(Users.role == 'student' and Users.active == 1).count()
    guest_cnt = db_sess.query(Users).filter(Users.role == 'guest' and Users.active == 1).count()
    active_cnt = teacher_cnt + student_cnt
    inactive_cnt = db_sess.query(Users).filter(Users.active == 0).count()
    return render_page(['admin'], '/admin/dashboard', 'admin_dashboard.html',
                       classes=class_cnt,
                       active=active_cnt,
                       inactive=inactive_cnt,
                       teacher=teacher_cnt,
                       student=student_cnt,
                       guest=guest_cnt)


@app.route('/admin/users')
def admin_users():
    db_sess = db_session.create_session()
    users = db_sess.query(Users).all()
    return render_page(['admin'], '/admin/users', 'admin_users.html', users=users)


@app.route('/teacher/schedule')
def teacher_schedule():
    if not login_fresh():
        return render_403()
    else:
        print(current_user.name)
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == current_user.login and Users.active == 1).first()
        if user.role == 'admin' or user.role == 'teacher':
            days = {'Понедельник': ['Математика', 'Русский язык', 'Окружающий мир', 'Литература', '-'],
                    'Вторник': ['ИЗО', 'Математика', 'Русский язык', 'Физ-ра', 'Английский язык'],
                    'Среда': ['История', 'Информатика', 'Русский язык', 'Технология', '-'],
                    'Четверг': ['География', 'Физ-ра', 'Математика', 'Русский язык', '-'],
                    'Пятница': ['Окружающий мир', 'Математика', 'Музыка', 'Литература', '-']
                    }
            return render_template('teacher_schedule.html', days=days)
        else:
            return render_403()


@app.route('/teacher/homework', methods=['POST', 'GET'])
def teacher_homework():
    if request.method == 'GET':
        return render_template('teacher_homework.html')
    elif request.method == 'POST':
        rec_dict = {
            'subject': request.form['subject'],
            'date': request.form['date'],
            'homework': request.form['homework'],
        }
        return render_template('teacher_show_homework.html',
                               subject=rec_dict['subject'],
                               date=rec_dict['date'],
                               homework=rec_dict['homework'])


@app.route('/student/diary')
def student_diary():
    days = {'Понедельник': [['Математика', '...'], ['Русский язык', '..'], ['Окружающий мир', ''], ['Литература', ''],
                            ['', '']],
            'Вторник': [['ИЗО', '.'], ['Математика', '...'], ['Русский язык', ''], ['Физ-ра', ''],
                        ['Английский язык', '.']],
            'Среда': [['История', '.'], ['Информатика', ''], ['Русский язык', '.'], ['Технология', '..'], ['', '']],
            'Четверг': [['География', '..'], ['Физ-ра', '.'], ['Математика', ''], ['Русский язык', '.'], ['', '']],
            'Пятница': [['Окружающий мир', '..'], ['Математика', '....'], ['Музыка', '..'], ['Литература', '..'],
                        ['', '']]
            }
    return render_template('student_diary.html', days=days)


@app.route('/student/schedule')
def student_schedule():
    # for user in session.query(Students).filter(Students.name.like('%Вася%')):
    #    d_us = user.class_id.schedule
    #    print(loads(d_us))
    days = {'Понедельник': ['Математика', 'Русский язык', 'Окружающий мир', 'Литература', '-'],
            'Вторник': ['ИЗО', 'Математика', 'Русский язык', 'Физ-ра', 'Английский язык'],
            'Среда': ['История', 'Информатика', 'Русский язык', 'Технология', '-'],
            'Четверг': ['География', 'Физ-ра', 'Математика', 'Русский язык', '-'],
            'Пятница': ['Окружающий мир', 'Математика', 'Музыка', 'Литература', '-']
            }
    return render_template('student_schedule.html', days=days)


@app.route('/student/grade')
def student_grade():
    grades = {'subg1': [5, 4, 3, 5], 'subg2': [5, 4, 5, 5, 5, 5],
              'subg3': [5, 4, 4, 4, 5]
              }
    grd_sum = {'subg1': round(sum(grades['subg1']) / len(grades['subg1']), 2),
               'subg2': round(sum(grades['subg2']) / len(grades['subg2']), 2),
               'subg3': round(sum(grades['subg3']) / len(grades['subg3']), 2)}
    return render_template('student_grade.html', grades=grades, grd_sum=grd_sum)


@app.route('/student/profile')
def student_profile():
    return render_template('student_profile.html')


def get_menu(role):
    """
    Возвращает список пунктов меню, доступных роли.
    :param role:
    :return:
    """
    db_sess = db_session.create_session()
    items = db_sess.query(Menu).filter(Menu.roles.ilike(f'%{role}%')).all()
    menu = dict()
    section = ""
    for item in items:
        if item.section:
            arr = menu.get(section)
            arr.append(item)
            menu[section] = arr
        else:
            section = item.title
            menu[section] = []
    return menu


def render_page(roles, ref, template, **context):
    """
    Рендерит страницы.
    :param roles список ролей, которым доступна страница
    :param ref адрес страницы
    :param template имя шаблона
    :param context список переменных для передачи в шаблон
    :return:
    """
    if not login_fresh():
        return render_403()
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == current_user.login and Users.active == 1).first()
        if user.role in roles:
            menu = get_menu(user.role)
            if not context:
                context = dict()
            context["menu"] = menu
            context["ref"] = ref
            context["role"] = user.role
            context["username"] = f"{user.name} {user.surname[0]}."
            return render_template(template, **context)
        else:
            return render_403()


def render_403():
    """
    Рендерит страницу 403.
    :return:
    """
    return render_template('page_error.html',
                           number="403",
                           header="Access denied",
                           description="Для доступа к этой странице надо авторизоваться")


app.run(port=8080, host='127.0.0.1', debug=True)

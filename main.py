import datetime
import json
from json import loads

from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_fresh
from flask_restful import reqparse, abort, Api, Resource
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

from data import db_session
from data.classes import Classes
from data.grades import Grade
from data.homeworks import Homeworks
from data.menu import Menu
from data.role import Role
from data.users import Users

app = Flask('MyApp')
api = Api(app)
app.config['SECRET_KEY'] = 'brbrbr'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/school.db")
session = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    return session.query(Users).get(user_id)


class LoginForm(FlaskForm):
    """
    Форма логина пользователя.
    """
    identifier = StringField()
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisrationForm(FlaskForm):
    """
    Форма регистрации пользователя.
    """
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
    """
    Страница логина/регистрации пользователя.
    :return:
    """
    if not login_fresh():
        formL = LoginForm()
        formR = RegisrationForm()
        if formL.identifier.data == 'LOGIN' and formL.validate_on_submit():
            user = session.query(Users).filter(Users.login == formL.username.data and Users.active == 1).first()
            if user and user.password == formL.password.data:
                if user.role == 'guest':
                    return render_template('page_guest.html', name=user.name, surname=user.surname)
                else:
                    role = session.query(Role).filter(Role.name == user.role).first()
                    login_user(user)
                    return redirect(f"/{role.start_page}")
            return render_template('login_form.html',
                                   message="Неправильный логин или пароль",
                                   formL=formL, formR=formR)
        if formR.identifier.data == 'REGISTRATION' and formR.validate_on_submit():
            user = session.query(Users).filter(Users.login == formR.username.data).first()
            if user:
                return render_template('login_form.html',
                                       message="Такой логин уже занят",
                                       formL=formL, formR=formR)
            if not formR.password.data == formR.confirm_password.data:
                return render_template('login_form.html',
                                       message="Пароли должны совпадать",
                                       formL=formL, formR=formR)
            new_user = Users()
            new_user.name = formR.name.data
            new_user.surname = formR.surname.data
            new_user.otchestvo = formR.otchestvo.data
            new_user.login = formR.username.data
            new_user.password = formR.password.data
            new_user.role = "guest"
            new_user.active = 1
            new_user.class_id = 1
            session.add(new_user)
            session.commit()
            return render_template('page_guest.html', name=formR.name.data, surname=formR.surname.data)
        return render_template('login_form.html', formL=formL, formR=formR)
    else:
        user = session.query(Users).filter(Users.login == current_user.login and Users.active == 1).first()
        role = session.query(Role).filter(Role.name == user.role).first()
        if role == 'guest':
            return render_template('page_guest.html', name=user.name, surname=user.surname)
        else:
            return redirect(f"/{role.start_page}")


@app.route('/logout', methods=['GET'])
def logout():
    """
    Выход пользователя.
    :return:
    """
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    """
    Ошибка 404 - PAGE NOT FOUND
    :param e:
    :return:
    """
    return render_template('page_error.html',
                           number="404",
                           header="Page not found",
                           description="Извините, но мы не смогли найти эту страницу"), 404


@app.route('/admin/dashboard')
def admin_dashboard():
    """
    Страница с дашбордом админа.
    :return:
    """
    class_cnt = session.query(Classes).count()
    teacher_cnt = session.query(Users).filter(Users.role == 'teacher' and Users.active == 1).count()
    student_cnt = session.query(Users).filter(Users.role == 'student' and Users.active == 1).count()
    guest_cnt = session.query(Users).filter(Users.role == 'guest' and Users.active == 1).count()
    active_cnt = teacher_cnt + student_cnt
    inactive_cnt = session.query(Users).filter(Users.active == 0).count()
    return render_page(['admin'], '/admin/dashboard', 'admin_dashboard.html',
                       classes=class_cnt,
                       active=active_cnt,
                       inactive=inactive_cnt,
                       teacher=teacher_cnt,
                       student=student_cnt,
                       guest=guest_cnt)


class UserEditForm(FlaskForm):
    """
    Форма редактирования пользователя для страницы /admin/users
    """
    identifier = StringField()
    id = StringField('ID')
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    otchestvo = StringField('Отчество')
    role = StringField('Роль')
    class_id = StringField('ID класса')
    active = BooleanField('Активен')


@app.route('/admin/users', methods=['POST', 'GET'])
def admin_users():
    """
    Страница просмотра/редактрования пользователей для администратора
    :return:
    """
    form = UserEditForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # сохраним данные
            user = session.query(Users).get(form.id.data)
            if user:
                user.surname = form.surname.data
                user.name = form.name.data
                user.otchestvo = form.otchestvo.data
                user.role = form.role.data
                user.class_id = form.class_id.data
                user.active = 1 if form.active.data else 0
                session.commit()
                return redirect("/admin/users")
            else:
                print(f"Что-то пошло не так... Пользоватеь с id={form.id.data} не найден!")
    # Начитаем данные и заустим страницу
    users = session.query(Users.id,
                          Users.class_id,
                          Users.name,
                          Users.otchestvo,
                          Users.surname,
                          Users.login,
                          Users.role,
                          Users.active,
                          Classes.number,
                          Classes.letter).filter(Users.class_id == Classes.cl_id).all()
    # print("JSON:", json.dumps([x.__json__() for x in users]))
    # jsonify([x.__json__() for x in users])
    return render_page(['admin'], '/admin/users', 'admin_users.html', users=users, form=form)


@app.route('/teacher/schedule')
def teacher_schedule():
    """
    Страница расписания занятий для учителя
    :return:
    """
    clas = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
    sch = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().schedule)
    days = {'Понедельник': [x for x in sch['mon']],
            'Вторник': [x for x in sch['tue']],
            'Среда': [x for x in sch['wed']],
            'Четверг': [x for x in sch['thu']],
            'Пятница': [x for x in sch['fri']]
            }
    rngs = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().time_schedule)
    times = rngs['day']
    return render_page(['admin', 'teacher'], '/teacher/schedule', 'teacher_schedule.html', days=days, times=times, clas=clas)


@app.route('/teacher/homework/<n>', methods=['POST', 'GET'])
def teacher_homework(n):
    """
    Страница вввода домашних заданий для учителя
    :return:
    """
    cls_cur = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
    if request.method == 'POST':
        subj = request.form['subj']
        date = request.form['date']
        homework = request.form['homework']
        hw = session.query(Homeworks).filter(Homeworks.class_id == cls_cur.cl_id, Homeworks.subject == subj, Homeworks.date == date).first()
        if hw:
            hw.homework = homework
        else:
            hw = Homeworks()
            hw.class_id = cls_cur.cl_id
            hw.date = date
            hw.subject = subj
            hw.homework = homework
            session.add(hw)
        session.commit()
        return redirect(f"/teacher/homework/{n}")
    class_name = str(cls_cur.number) + '-' + cls_cur.letter
    today = datetime.datetime.today()
    today_weekday = datetime.datetime.today().weekday()
    week_dates = {'Понедельник': str(today - datetime.timedelta(days=(today_weekday - 0 - (int(n) * 7)))).split(' ')[0],
                  'Вторник': str(today - datetime.timedelta(days=(today_weekday - 1 - (int(n) * 7)))).split(' ')[0],
                  'Среда': str(today - datetime.timedelta(days=(today_weekday - 2 - (int(n) * 7)))).split(' ')[0],
                  'Четверг': str(today - datetime.timedelta(days=(today_weekday - 3 - (int(n) * 7)))).split(' ')[0],
                  'Пятница': str(today - datetime.timedelta(days=(today_weekday - 4 - (int(n) * 7)))).split(' ')[0],
                  'Суббота': str(today - datetime.timedelta(days=(today_weekday - 5 - (int(n) * 7)))).split(' ')[0],
                  'Воскресенье': str(today - datetime.timedelta(days=(today_weekday - 6 - (int(n) * 7)))).split(' ')[0]}
    sch = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().schedule)

    days = {'Понедельник': [[x, session.query(Homeworks).filter(Homeworks.date == week_dates['Понедельник'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first()] for x in sch['mon']],
            'Вторник': [[x, session.query(Homeworks).filter(Homeworks.date == week_dates['Вторник'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first()] for x in sch['tue']],
            'Среда': [[x, session.query(Homeworks).filter(Homeworks.date == week_dates['Среда'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first()] for x in sch['wed']],
            'Четверг': [[x, session.query(Homeworks).filter(Homeworks.date == week_dates['Четверг'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first()] for x in sch['thu']],
            'Пятница': [[x, session.query(Homeworks).filter(Homeworks.date == week_dates['Пятница'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first()] for x in sch['fri']]
            }
    rngs = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().time_schedule)
    times = rngs['day']
    return render_page(['admin', 'teacher'], '/teacher/homework/0', 'teacher_homework.html',
                       class_name=class_name,
                       days=days,
                       week_dates=week_dates,
                       n=int(n),
                       datetime=datetime.datetime,
                       times=times)


@app.route('/teacher/grade/<subj>', methods=['POST', 'GET'])
def teacher_grade(subj):
    if request.method == 'POST':
        gr = Grade()
        gr.date = request.form['date']
        gr.subject = subj
        gr.user_id = request.form['id']
        gr.grade = request.form['grade']
        gr.reason = request.form['reason']
        session.add(gr)
        session.commit()
        return redirect(f"/teacher/grade/{subj}")
    elif request.method == 'GET':
        cls_cur = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
        class_name = str(cls_cur.number) + '-' + cls_cur.letter
        lst_obj = ['Русский', 'Английский', 'Алгебра', 'Литература', 'Информатика', 'ИЗО', 'Физ-ра', 'Музыка']
        reason_obj = ['Домашняя работа', 'Работа в классе', 'Самостоятельная', 'Контрольная']
        std_all_inf = session.query(Users).filter(Users.class_id == current_user.class_id,
                                                  Users.role == 'student').all()
        grades_list = dict()
        for std in std_all_inf:
            key = f'{std.surname} {std.name} {std.otchestvo}'
            grades_list[key] = session.query(Grade).filter(Grade.user_id == std.id, Grade.subject == subj).all()
            if grades_list[key] is None:
                grades_list[key] = list()
            else:
                grades_std = list()
                for d in grades_list[key]:
                    grades_std.append([d.grade, d.reason, d.date])
                grades_list[key] = (grades_std, std.id)
        students = list()
        for k in grades_list.keys():
            if len(grades_list[k]) != 0:
                grades, id = grades_list[k]
                students.append([k, grades, round(0 if len(grades) == 0 else sum([x[0] for x in grades]) / len(grades), 2), id])
            else:
                students.append([k, '', 0.0])
        return render_page(['admin', 'teacher'], '/teacher/grade/Русский', 'teacher_grade.html',
                           class_name=class_name,
                           students=students,
                           obj=subj,
                           lst_obj=lst_obj,
                           reason_obj=reason_obj)


@app.route('/student/diary/<n>')
def student_diary(n):
    """
    Дневник ученика
    :return:
    """
    cls_cur = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
    class_name = str(cls_cur.number) + '-' + cls_cur.letter
    today = datetime.datetime.today()
    today_weekday = datetime.datetime.today().weekday()
    week_dates = {'Понедельник': str(today - datetime.timedelta(days=(today_weekday - 0 - (int(n) * 7)))).split(' ')[0],
                  'Вторник': str(today - datetime.timedelta(days=(today_weekday - 1 - (int(n) * 7)))).split(' ')[0],
                  'Среда': str(today - datetime.timedelta(days=(today_weekday - 2 - (int(n) * 7)))).split(' ')[0],
                  'Четверг': str(today - datetime.timedelta(days=(today_weekday - 3 - (int(n) * 7)))).split(' ')[0],
                  'Пятница': str(today - datetime.timedelta(days=(today_weekday - 4 - (int(n) * 7)))).split(' ')[0],
                  'Суббота': str(today - datetime.timedelta(days=(today_weekday - 5 - (int(n) * 7)))).split(' ')[0],
                  'Воскресенье': str(today - datetime.timedelta(days=(today_weekday - 6 - (int(n) * 7)))).split(' ')[0]}
    sch = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().schedule)

    days = {'Понедельник': [[x,
                             session.query(Homeworks).filter(Homeworks.date == week_dates['Понедельник'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first(),
                             session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == x, Grade.date == week_dates['Понедельник']).all()
                             ] for x in sch['mon']],
            'Вторник': [[x,
                         session.query(Homeworks).filter(Homeworks.date == week_dates['Вторник'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first(),
                         session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == x, Grade.date == week_dates['Вторник']).all()
                         ] for x in sch['tue']],
            'Среда': [[x,
                       session.query(Homeworks).filter(Homeworks.date == week_dates['Среда'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first(),
                       session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == x, Grade.date == week_dates['Среда']).all()
                       ] for x in sch['wed']],
            'Четверг': [[x,
                         session.query(Homeworks).filter(Homeworks.date == week_dates['Четверг'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first(),
                         session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == x, Grade.date == week_dates['Четверг']).all()
                         ] for x in sch['thu']],
            'Пятница': [[x,
                         session.query(Homeworks).filter(Homeworks.date == week_dates['Пятница'], Homeworks.subject == x, Homeworks.class_id == cls_cur.cl_id).first(),
                         session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == x, Grade.date == week_dates['Пятница']).all()
                         ] for x in sch['fri']]
            }
    rngs = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().time_schedule)
    times = rngs['day']
    return render_page(['admin', 'student'], '/student/diary/0', 'student_diary.html',
                       class_name=class_name,
                       days=days,
                       week_dates=week_dates,
                       n=int(n),
                       datetime=datetime.datetime,
                       times=times)


@app.route('/student/schedule')
def student_schedule():
    """
    Страница расписания занятий для учеников
    :return:
    """
    clas = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
    sch = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().schedule)
    days = {'Понедельник': [x for x in sch['mon']],
            'Вторник': [x for x in sch['tue']],
            'Среда': [x for x in sch['wed']],
            'Четверг': [x for x in sch['thu']],
            'Пятница': [x for x in sch['fri']]
            }
    rngs = loads(session.query(Classes).filter(Classes.cl_id == current_user.class_id).first().time_schedule)
    times = rngs['day']
    return render_page(['admin', 'student'], '/student/schedule', 'teacher_schedule.html', days=days, times=times, clas=clas)


@app.route('/student/grade')
def student_grade():
    lst_subj = ['Русский', 'Английский', 'Алгебра', 'Литература', 'Информатика', 'ИЗО', 'Физ-ра', 'Музыка']
    grades = dict()
    grd_sum = dict()
    for subj in lst_subj:
        grades[subj] = session.query(Grade).filter(Grade.user_id == current_user.id, Grade.subject == subj).all()
        grades_list = [] if len(grades[subj]) == 0 else [x.grade for x in grades.get(subj)]
        grd_sum[subj] = round(0 if len(grades_list) == 0 else sum(grades_list) / len(grades_list), 2)
    return render_page(['admin', 'student'], '/student/grade', 'student_grade.html', grades=grades, grd_sum=grd_sum)


@app.route('/profile')
def student_profile():
    cur_cl = session.query(Classes).filter(Classes.cl_id == current_user.class_id).first()
    data = {'имя': current_user.name,
            'фамилия': current_user.surname,
            'отчество': current_user.otchestvo,
            'статус': 'администратор' if current_user.role == 'admin' else 'учитель' if current_user.role == 'teacher' else 'ученик',
            'класс': str(cur_cl.number) + '-' + cur_cl.letter,
            'role': current_user.role,
            'login': current_user.login
            }
    return render_page(['admin', 'teacher', 'student'], '/profile', 'page_profile.html', data=data)


def get_menu(role):
    """
    Возвращает список пунктов меню, доступных роли.
    :param role:
    :return:
    """
    items = session.query(Menu).filter(Menu.roles.ilike(f'%{role}%')).all()
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
        if current_user.role in roles:
            menu = get_menu(current_user.role)
            if not context:
                context = dict()
            context["menu"] = menu
            context["ref"] = ref
            context["role"] = current_user.role
            context["username"] = f"{current_user.name} {current_user.surname[0]}."
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


class AllInf(Resource):
    def get(self, cls_nl):
        if len(cls_nl) < 2:
            return jsonify({'Класс отсутствует': None})
        cls = session.query(Classes).filter(Classes.number == int(cls_nl[0]),
                                                  Classes.letter == cls_nl[1]).first()
        if cls is None:
            return jsonify({'Класс отсутствует': None})
        students = session.query(Users).filter(Users.class_id == cls.cl_id, Users.role == 'student', Users.active == 1).all()
        cls_dict = dict()
        teacher = session.query(Users).filter(Users.class_id == cls.cl_id, Users.role == 'teacher', Users.active == 1).first()
        if teacher is not None:
            cls_dict['teachers'] = [{'surname': teacher.surname, 'name': teacher.name, 'otchestvo': teacher.otchestvo}]
        else:
            cls_dict['teachers'] = None
        if students is not None:
            cls_dict['students'] = list()
            for std in students:
                cls_dict['students'].append({'surname': std.surname, 'name': std.name, 'otchestvo': std.otchestvo})
        else:
            cls_dict['students'] = None
        sch = loads(session.query(Classes).filter(Classes.cl_id == cls.cl_id).first().schedule)
        cls_dict['schedule'] = {'Понедельник': [x for x in sch['mon']],
                                'Вторник': [x for x in sch['tue']],
                                'Среда': [x for x in sch['wed']],
                                'Четверг': [x for x in sch['thu']],
                                'Пятница': [x for x in sch['fri']]
                                }
        return jsonify(cls_dict)


api.add_resource(AllInf, '/api/<cls_nl>')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)

from json import dumps
from data import db_session
import datetime as dt
from data.classes import Classes
from data.homeworks import Homeworks
from data.menu import Menu
from data.role import Role
from data.users import Users

db_session.global_init('db/school.db')
session = db_session.create_session()

# КЛАССЫ
clas = Classes()
clas.number = 5
clas.letter = 'А'
clas.schedule = dumps({"mon": ["Алгебра", "Литература", "Информатика", "Английский"],
                       "tue": ["Физ-ра", "География", "Литература", "Физика", "История"],
                       "wed": ["Русский", "Геометрия", "География", "Химия", "Биология"],
                       "thu": ["Литература", "Физ-ра", "Информатика", "Английский"],
                       "fri": ["Биология", "Русский", "Музыка", "ИЗО"]})
clas.time_schedule = dumps({"day": ["08:00", "08:50", "09:40", "10:40", "11:30"]})
session.add(clas)

clas = Classes()
clas.number = 5
clas.letter = 'Б'
clas.schedule = dumps({"mon": ["Литература", "Информатика", "Английский", "Алгебра"],
                       "tue": ["География", "Литература", "Физика", "История", "Физ-ра"],
                       "wed": ["Геометрия", "География", "Химия", "Биология", "Русский"],
                       "thu": ["Физ-ра", "Информатика", "Английский", "Литература"],
                       "fri": ["Русский", "Музыка", "ИЗО", "Биология"]})
clas.time_schedule = dumps({"day": ["08:00", "08:50", "09:40", "10:40", "11:30"]})
session.add(clas)

# ДОМАШКИ
hm = Homeworks()
hm.date = '2022-04-11'
hm.subject = 'Алгебра'
hm.class_id = 1
hm.homework = 'Номер 1, 2 и 3 стр. 115'
session.add(hm)

# ПОЛЬЗОВАТЕЛИ
st0 = Users()
st0.name = 'Юля'
st0.surname = 'Полякова'
st0.otchestvo = 'Александровна'
st0.role = 'admin'
st0.login = 'admin'
st0.password = 'wizard'
st0.class_id = 1
st0.active = 1
session.add(st0)

st1 = Users()
st1.name = 'Вася'
st1.surname = 'Пупкин'
st1.otchestvo = 'Владимирович'
st1.role = 'student'
st1.login = 'Васька'
st1.password = 'Пупкин'
st1.class_id = 1
st1.active = 1
session.add(st1)

st2 = Users()
st2.name = 'Пупка'
st2.surname = 'Васькин'
st2.otchestvo = 'Мировладович'
st2.role = 'student'
st2.login = 'Пупка'
st2.password = 'Васькин'
st2.class_id = 1
st2.active = 1
session.add(st2)

th = Users()
th.name = 'Марья'
th.surname = 'Щербакова'
th.otchestvo = 'Ивановна'
th.role = 'teacher'
th.login = 'maria'
th.password = 'teacher-1'
th.class_id = 1
th.active = 1
session.add(th)

# РОЛИ
r1 = Role()
r1.name = 'admin'
r1.start_page = 'admin/dashboard'
session.add(r1)

r2 = Role()
r2.name = 'teacher'
r2.start_page = 'teacher/schedule'
session.add(r2)

r3 = Role()
r3.name = 'student'
r3.start_page = 'student/diary/0'
session.add(r3)

r4 = Role()
r4.name = 'guest'
r4.start_page = '/'
session.add(r4)

# МЕНЮ
item = Menu()
item.name = "admin-section"
item.title = "Администратор"
item.roles = "admin"
item.order = 0
session.add(item)

item = Menu()
item.name = "dashboard"
item.section = "admin-section"
item.title = "Дашборд"
item.icon = "fa fa-dashboard"
item.ref = "/admin/dashboard"
item.roles = "admin"
item.order = 1
session.add(item)

item = Menu()
item.name = "users"
item.section = "admin-section"
item.title = "Пользователи"
item.icon = "fa fa-users"
item.ref = "/admin/users"
item.roles = "admin"
item.order = 2
session.add(item)

item = Menu()
item.name = "teacher-section"
item.title = "Учитель"
item.roles = "admin|teacher"
item.order = 10
session.add(item)

item = Menu()
item.name = "schedule"
item.section = "teacher-section"
item.title = "Расписание"
item.icon = "fa fa-tasks"
item.ref = "/teacher/schedule"
item.roles = "admin|teacher"
item.order = 11
session.add(item)

item = Menu()
item.name = "homework"
item.section = "teacher-section"
item.title = "Домашнее задание"
item.icon = "fa fa-briefcase"
item.ref = "/teacher/homework/0"
item.roles = "admin|teacher"
item.order = 12
session.add(item)

item = Menu()
item.name = "grade"
item.section = "teacher-section"
item.title = "Оценки"
item.icon = "fa fa-graduation-cap"
item.ref = "/teacher/grade/Русский"
item.roles = "admin|teacher"
item.order = 13
session.add(item)

item = Menu()
item.name = "student-section"
item.title = "Ученик"
item.roles = "admin|student"
item.order = 20
session.add(item)

item = Menu()
item.name = "diary"
item.section = "student-section"
item.title = "Дневник"
item.icon = "fa fa-book"
item.ref = "/student/diary/0"
item.roles = "admin|student"
item.order = 21
session.add(item)

item = Menu()
item.name = "schedule"
item.section = "student-section"
item.title = "Расписание"
item.icon = "fa fa-tasks"
item.ref = "/student/schedule"
item.roles = "admin|student"
item.order = 22
session.add(item)

item = Menu()
item.name = "grade"
item.section = "student-section"
item.title = "Оценки"
item.icon = "fa fa-graduation-cap"
item.ref = "/student/grade"
item.roles = "admin|student"
item.order = 23
session.add(item)

session.commit()

import psycopg2
from FDataBase import FDataBase
from config import host, user, password, dbname
from flask import Flask, render_template, g, request, flash, redirect, session, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
from admin.admin import admin


app = Flask(__name__)

app.config['SECRET_KEY'] = 'asdf1asdf2asdf3'

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа на сайте"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=dbname
    )
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# @app.route('/')
# def hello_world():
#     db = get_db()
#     return render_template('index.html', menu=menu)


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


menu = [{"name": "Главная", "url": "/"},
        {"name": "Добавить товар", "url": 'add_goods'},
        {"name": "Товары", "url": 'get_goods'},
        {"name": "Корзина", "url": "get_cart"},
        {"name": "Добавить в корзину", "url": 'add_cart'},
        {"name": "Авторизация", "url": "login"}]


@app.route("/")
def index():
    return render_template('index.html', menu=menu)


@app.route("/add_goods", methods=["POST", "GET"])
@login_required
def addGoods():
    # if request.method == 'POST':
    #     if len(request.form['name'])>0 and len(request.form['desc'])>0:
    #         res = dbase.addGoods(request.form['name'], request.form['desc'], request.form['price'])
    #         print(res)
    #         if not res:
    #             flash(' ошибка добавления товара', category='error')
    #         else:
    #             flash(' товар добавлен', category='success')
    #     else:
    #         flash(' ошибка добавления товара', category='error')
    # return render_template('add_goods.html', menu=menu, title='Добавление товара')
    return redirect(url_for('noaccess'))


@app.route("/get_goods")
@login_required
def getGoods():
    res = dbase.getGoods()
    if not res:
        abort(404)
    return render_template('get_goods.html', menu=menu, title='Товары', res=res)


@app.route("/add_cart", methods=["POST", "GET"])
@login_required
def addCart():
    if request.method == 'POST':
        if len(request.form['status']) > 0:
            res = dbase.addCart(request.form['date_published'], request.form['date_sent'],
                                request.form['status'], request.form['id_goods'])
            print(res)
            if not res:
                flash('ошибка добавления товара', category='error')
            else:
                flash('товар добавлен', category='success')
        else:
            flash(' ошибка добавления товара', category='error')
    return render_template('add_cart.html', menu=menu, title='Добавление товара')


@app.route("/get_cart")
@login_required
def getCart():
    res = dbase.getCart()
    print(res)
    if res == []:
        return redirect(url_for('empty'))
    if not res:
        abort(404)
    return render_template('get_cart.html', menu=menu, title='Корзина', res=res)


@app.route('/empty')
def empty():
    return f''' <p> В корзине пусто
                <p><a href="{url_for('getGoods')}"> Смотреть товары </a>'''


@app.route("/about")
def about():
    print(dbase.getGoods())
    return render_template('about.html', title='о сайте', menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])

        if user and user[4] == request.form['psw']:
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(url_for('profile'))

        flash('Неверные логин/пароль', 'error')
    return render_template('login.html', title='Авторизация', menu=menu)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    return render_template('profile.html', title='Профиль', menu=menu)


@app.route('/noaccess')
def noaccess():
    return render_template('noaccess.html', title='NO ACCESS LEVEL', menu=menu)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        if len(request.form['username']) > 4 and len(request.form['email']) > 4 and len(request.form['psw']) > 4 and (
                request.form['psw'] == request.form['psw2']):

            res = dbase.addUser(request.form['username'], request.form['email'], request.form['address'],
                                request.form['psw'])
            print(res)
            if res:
                flash('Вы успешно зарегестрированы', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при добавлении в бд', 'error')
        else:
            flash('Неверные поля регистрации', 'error')
    return render_template('register.html', title='Регистрация', menu=menu)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='страница не найдена', menu=menu), 404


if __name__ == '__main__':
    app.run(debug=True)

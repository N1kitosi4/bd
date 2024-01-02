from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
import psycopg2
from FDataBase import *

admin = Blueprint('admin', __name__, template_folder='templates')


def login_admin():
    session['admin_logged'] = True


def isLogged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)


menu = [{'url': '.richord', 'title': 'Богатые'},
        {'url': '.listgoods', 'title': 'Товары'},
        {'url': '.addgoods', 'title': 'Добавить т'},
        {'url': '.updgoods', 'title': 'Обновить т'},
        {'url': '.delgoods', 'title': 'Удалить т'},
        {'url': '.view', 'title': 'Товары в з'},
        {'url': '.updorders', 'title': 'Обновить цену з'},
        {'url': '.delorders', 'title': 'Удалить з'},
        {'url': '.logout', 'title': 'Выйти'}]

db = None


@admin.before_request
def before_request():
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@admin.route("/")
def index():
    if not isLogged():
        return redirect(url_for('.index'))
    return render_template('admin/index.html', menu=menu, title=' Админ ')


@admin.route("/login", methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['psw'] == 'admin':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('Неверные логин/пароль', 'error')
    return render_template('admin/login.html', title='Админка')


@admin.route("/logout", methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))


@admin.route('/listgoods')
def listgoods():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT goods_id, name_goods, description, price FROM goods ORDER BY goods_id;")
            list = cur.fetchall()

        except psycopg2.Error as e:
            print("Ошибка получения из БД " + str(e))

    return render_template('admin/listgoods.html', title='Список товаров', menu=menu, list=list)


@admin.route('/view')
def view():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT * FROM get_gio;")
            list = cur.fetchall()

        except psycopg2.Error as e:
            print("Ошибка получения из БД " + str(e))

    return render_template('admin/view.html', title='Список товаров в заказе', menu=menu, list=list)


@admin.route('/add', methods=["POST", "GET"])
def addgoods():
    if not isLogged():
        return redirect(url_for('.login'))

    if request.method == 'POST':
        if len(request.form['name']) > 0 and len(request.form['desc']) > 0:
            cur = db.cursor()
            cur.execute(f"INSERT INTO goods(name_goods, description, price) VALUES (%s, %s, %s)",
                        [request.form['name'], request.form['desc'], request.form['price']])
            db.commit()
            if not cur:
                flash(' ошибка добавления товара', category='error')
            else:
                flash(' товар добавлен', category='success')
        else:
            flash('ошибка добавления товара', category='error')
    return render_template('admin/add.html', menu=menu, title='Добавление товара')


@admin.route('/del', methods=["POST", "GET"])
def delgoods():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"CALL delete_g({int(request.form['goods_id'])})")
        db.commit()
        db.close()
        if not cur:
            flash('ошибка удаления товара', category='error')
        else:
            flash('товар удален', category='success')
    return render_template('admin/del.html', menu=menu, title='Удаление товара')


@admin.route('/upd', methods=["POST", "GET"])
def updgoods():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"CALL update_g({int(request.form['goods_id'])}, {float(request.form['price'])})")
        db.commit()
        db.close()
        if not cur:
            flash('ошибка обновления товара', category='error')
        else:
            flash('товар обновлен', category='success')
    return render_template('admin/upd.html', menu=menu, title='Обновление товара')


@admin.route('/updord', methods=["POST", "GET"])
def updorders():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"CALL update_ord_cost({int(request.form['id_users'])})")
        db.commit()
        db.close()
        if not cur:
            flash('ошибка обновления заказа', category='error')
        else:
            flash('заказ обновлен', category='success')
    return render_template('admin/updord.html', menu=menu, title='Обновление заказа')


@admin.route('/delorders', methods=["POST", "GET"])
def delorders():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"CALL delete_ord()")
        db.commit()
        #db.close()
        if not cur:
            flash('ошибка удаления заказа', category='error')
        else:
            flash('заказ удален', category='success')
    return render_template('admin/delorders.html', menu=menu, title='Удаление заказа')


@admin.route('/richord')
def richord():
    if not isLogged():
        return redirect(url_for('.login'))
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT * FROM rich_orders();")
            list = cur.fetchall()
        except psycopg2.Error as e:
            print("Ошибка получения заказа из БД " + str(e))
    return render_template('admin/richord.html', menu=menu, title='Дорогие заказы', list=list)

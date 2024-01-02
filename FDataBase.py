import psycopg2
from flask_login import current_user
from UserLogin import UserLogin


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addUser(self, name, email, address, hpassw):
        try:
            self.__cur.execute(f"SELECT COUNT(email) FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            print(res)
            if res[0] > 0:
                print('пользователь уже есть')
                return False

            self.__cur.execute("INSERT INTO users(users_name, email, address, passw) VALUES (%s, %s, %s, %s)",
                               [name, email, address, hpassw])
            self.__db.commit()
        except psycopg2.Error as e:
            print(' ошибка добавления в бд ' + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE users_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except psycopg2.Error as e:
            print("ошибка получения данных из бд " + str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{(email)}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except psycopg2.Error as e:
            print("ошибка получения данных из бд " + str(e))
        return False

    def addGoods(self, name, desc, price):
        try:
            sql = f"CALL ins_into_goods({name}, {desc}, {price})"
            #self.__cur.execute("INSERT INTO goods(name_goods, description, price) VALUES (%s, %s, %s)",
            #                   [name, desc, price])
            self.__cur.execute(sql)
            self.__db.commit()
        except psycopg2.Error as e:
            print(' ошибка добавления в бд ' + str(e))
            return False

        return True

    def getGoods(self):
        sql = '''SELECT goods_id, name_goods, description, price FROM goods;'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except psycopg2.Error as e:
            print("Ошибка получения товара из бд" + str(e))
        return (False, False, False, False)

    def addCart(self, date_published, date_sent, status, id_goods):
        try:
            self.__cur.execute(
                "INSERT INTO orders(id_users, date_published, date_sent, status, id_goods) VALUES (%s, %s, %s, %s, %s)",
                [current_user.get_id(), date_published, date_sent, status, id_goods])
            self.__db.commit()
        except psycopg2.Error as e:
            print(' ошибка добавления в бд ' + str(e))
            return False

        return True

    def getCart(self):
        sql = f"SELECT name_goods, description, date_published, date_sent, price, status, total_price FROM orders JOIN goods ON goods.goods_id = orders.id_goods WHERE id_users = {current_user.get_id()};"
        # sql = f"SELECT id_users, name_goods, total_price, status FROM goods_in_order JOIN goods ON goods.goods_id = goods_in_order.id_goods JOIN orders ON orders.orders_id = goods_in_order.id_orders WHERE id_users = {current_user.get_id()} GROUP BY orders_id, name_goods"
        #sql2 = f"CALL update_ord_cost({current_user.get_id()});"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:

                return res
        except psycopg2.Error as e:
            print("Ошибка получения товара из бд" + str(e))
        return []

    def delCart(self, orders_id):
        try:
            self.__cur.execute(
                f"DELETE FROM orders WHERE orders_id = {orders_id}")
            self.__db.commit()
        except psycopg2.Error as e:
            print(' ошибка добавления в бд ' + str(e))
            return False

        return True

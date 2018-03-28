import pymysql
import threading

def queries():
    threading.Timer(1.0, queries).start()
    conn1 = pymysql.connect(host='127.0.0.1',
                           user='root', passwd='minhkma',
                           db='information_schema')
    cur1 = conn1.cursor()
    for i in range(100):
        cur1.execute("SELECT (SELECT COUNT(*) FROM INNODB_CMPMEM) AS tot_user,"
                    "(SELECT COUNT(*) FROM INNODB_FT_CONFIG ) AS tot_cat,"
                    "(SELECT COUNT(*)FROM INNODB_SYS_TABLES) AS tot_course;")
    print(threading.current_thread().getName())
    conn1.close()


def inserts():
    threading.Timer(1.0, inserts).start()
    conn2 = pymysql.connect(host='127.0.0.1',
                           user='root', passwd='minhkma',
                           db='test')
    cur2 = conn2.cursor()
    for count_insert in range(100):
        cur2.execute("INSERT INTO animals (name) VALUES ('DOG');")
    conn2.close()
    print(threading.current_thread().getName())

queries()
inserts()

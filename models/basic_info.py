import pdb
import mysql.connector
import MySQLdb
import hashlib
import threading
import time
import random
import traceback
sem = threading.Semaphore()

from MySQLdb import cursors
import numpy as np



INF = (1 << 31)

passwd = "Data123?"

db = mysql.connector.connect(
    pool_name = "mypool",
    pool_size = 31,
    host='localhost',
    port=3306,
    user='charleshan',
    password=passwd,
    database='stu_union',
    charset='utf8',
    autocommit=True
)

a = 1

def db_execute(sql):
    # pdb.set_trace()
    flag = False
    global a

    try:
        db = mysql.connector.connect(
            pool_name = "mypool",
            pool_size = 31,
            host='localhost',
            port=3306,
            user='charleshan',
            password=passwd,
            database='stu_union',
            charset='utf8',
            autocommit=True
        )
        print(sql)
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            return None
        result = [result]
        while True:
            _ = cursor.fetchone()
            if _ is None:
                break
            result.append(_)
        
        
        result = np.array(result)
    except:
        flag = True
        print(traceback.print_exc())
        pass
    finally:
        cursor.close()
        db.close()

    
    if flag == True:
        assert(1 == 0)
    return result


def init_db(glo_db):
    global db
    db = glo_db

def calc_sha256(passwd):
    m = hashlib.sha256()
    m.update("{}".format(passwd).encode("ascii"))
    ret = "".join([chr(x % 26 + 97) for x in m.digest()])
    return ret

def db_init():
    try:
        sql = "create table sec_id_allocator ( \
            sec_id  int   not null, \
            primary key (sec_id)  \
        );"
        _ = db_execute(sql)
        

        sql = "insert into sec_id_allocator values (\"2\");"
        _ = db_execute(sql)
        
    except:
        pass

def new_sec_id():
    sql = "select * from sec_id_allocator;"
    result = db_execute(sql)
    result = result[0][0]
    ins_res = (result + 1) % INF
    sql = "update sec_id_allocator\
        set sec_id = \"{}\"\
        where sec_id = \"{}\";".format(ins_res, result)
    _ = db_execute(sql)
    
    return ins_res


def create_member_table():
    try:
        sql = "create table member ( \
            stu_id  int   not null, \
            stu_name  varchar(128)           , \
            passwd    varchar(512) ,  \
            contact   varchar(512) , \
            position  varchar(128) , \
            primary key (stu_id)  \
        );"
        _ = db_execute(sql)
        

        

        sql = "insert into member values (\"1234567890\", \"wenchen\", \"{}\", \"123456\", \"chair\");".format(calc_sha256("123456"))
        _ = db_execute(sql)
        
    except:
        pass

def create_section_table():
    try: 
        sql = "create table section (\
            section_id int not null, \
            section_name varchar(128), \
            member_limit int, \
            primary key (section_id) \
        );"
        _ = db_execute(sql)
        

        sql = "insert into section values (\"1\", \"admin\", \"0\");"
        _ = db_execute(sql)
        

    except:
        pass

def create_belong_section():
    try:
        sql = "create table belong ( \
            stu_id int not null, \
            section_id int,    \
            primary key (stu_id) \
        );"
        _ = db_execute(sql)
        

        sql = "insert into belong values (\"1234567890\", \"1\");"
        _ = db_execute(sql)
        
    except:
        pass

def section_name_exist(section_name):
    sql = "select section_name from section \
        where section_name = \"{}\";".format(section_name)
    
    result = db_execute(sql)
    return result != None

def section_exist(section_id):
    sql = "select section_id from section \
        where section_id = \"{}\";".format(section_id)
    
    result = db_execute(sql)
    return result != None

def member_exist(stu_id):
    sql = "select stu_id from member \
        where stu_id = \"{}\";".format(stu_id)
    
    result = db_execute(sql)
    return result != None

def get_belong(stu_id):
    # should first guarantee that this student is a member
    sql = "select section_id from belong \
        where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)[0][0]
    return result

def all_stu_belong(section_id):
    sql = "select stu_id from belong \
        where section_id = \"{}\";".format(section_id)
    result = db_execute(sql)
    return result

def authenticate(stu_id, passwd):
    passwd = calc_sha256(passwd)
    sql = "select member.stu_id, member.passwd, member.position, belong.section_id, member.stu_name, member.contact \
        from member, belong \
            where member.stu_id = belong.stu_id and \
            member.stu_id = \"{}\";".format(stu_id)
    

    result = db_execute(sql)
    if result is None or result[0][1] != passwd:
        return 401
    
    return 200, result[0][0], result[0][2], result[0][3], result[0][4], result[0][5]

def add_member(sess, stu_id, name, password, contact, position, section, passwd_origin=False):
    if sess["position"] != "chair" and (sess["position"] != "sec_head"):
        return 403
    
    if (member_exist(stu_id) == True):
        return 403

    if section_exist(section) == False:
        return 403
    
    if (sess["position"] == "sec_head" and get_belong(stu_id) != sess["section_id"]):
        return 403
    
    sql = "insert into member values (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\");".format(
        stu_id,
        name,
        calc_sha256(password) if passwd_origin == False else password,
        contact,
        position
    )
    _ = db_execute(sql)
    

    sql = "insert into belong values (\"{}\", \"{}\");".format(stu_id, section)
    _ = db_execute(sql)
    

    return 200


def delete_member(sess, stu_id):
    if sess["position"] != "chair" and sess["position"] != "sec_head":
        return 403
    if member_exist(stu_id) == False:
        return 404
    if (sess["position"] == "sec_head" and get_belong(stu_id) != sess["section_id"]):
        return 403

    sql = "delete from member \
        where stu_id = \"{}\";".format(stu_id)
    _ = db_execute(sql)
    

    sql = "delete from belong \
        where stu_id = \"{}\";".format(stu_id)
    _ = db_execute(sql)
    

    return 200
    



def create_section(sess, section_name):
    if sess["position"] != "chair":
        return 403
    if section_name_exist(section_name) == True:
        return 403
    section_id = new_sec_id()
    sql = "insert into section values (\"{}\", \"{}\", \"{}\")".format(section_id, section_name, 0)
    db_execute(sql)
    
    return 200


def delete_section(sess, section_id):
    if sess["position"] != "chair":
        return 403
    if section_exist(section_id) == False:
        return 404
    if all_stu_belong(section_id) != None:
        return 409
    sql = "delete from section \
        where section_id = \"{}\";".format(section_id)
    db_execute(sql)
    
    return 200

def update_section_name(sess, section_id, section_name):
    if sess["position"] != "chair":
        return 403
    if section_exist(section_id) == False:
        return 404
    sql = "update section \
        set section_name = \"{}\"\
        where section_id = \"{}\";".format(section_name, section_id)
    _ = db_execute(sql)
    
    return 200

def update_section_limit(sess, section_id, member_limit):
    if sess["position"] != "chair":
        return 403
    if section_exist(section_id) == False:
        return 404
    
    sql = "update section \
        set member_limit = \"{}\" \
        where section_id = \"{}\";".format(member_limit, section_id)
    _ = db_execute(sql)
    
    return 200

def query_section():
    sql = "select section.section_id, section.section_name, section.member_limit from section;"
    result = db_execute(sql)
    heads = []
    count = []

    for row in result:
        sql = "select count(*) from belong where belong.section_id = \"{}\"".format(row[0])
        res = db_execute(sql)
        count.append(res)

        sql = "select member.stu_id, stu_name from member, belong where member.stu_id = belong.stu_id and belong.section_id = \"{}\";".format(row[0])
        res = db_execute(sql)
        heads.append(res if res is not None else [])
    return result, count, heads

def query_member(stu_name, section_id, page_num):
    row_per_page = 20

    if page_num is None:
        page_num = 1
        row_per_page = INF

    if stu_name == "None" and section_id == -1:
        sql = "select member.stu_id, member.stu_name, belong.section_id, member.position, member.contact, member.passwd \
            from member, belong \
            where member.stu_id = belong.stu_id \
                order by member.stu_id"
        
    elif stu_name == "None":
        sql = "select member.stu_id, member.stu_name, belong.section_id, member.position, member.contact, member.passwd \
            from member, belong \
            where member.stu_id = belong.stu_id and \
                belong.section_id = \"{}\" \
                order by member.stu_id ;".format(section_id)
    else:
        sql = "select member.stu_id, member.stu_name, belong.section_id, member.position, member.contact, member.passwd \
            from member, belong \
            where member.stu_id = belong.stu_id and \
                member.stu_name = \"{}\" \
                order by member.stu_id ;".format(stu_name)

    result = db_execute(sql)

    l = row_per_page * (page_num - 1)
    r = l + row_per_page
    if (l >= len(result)):
        return []
    elif r >= len(result):
        return result[l: len(result)]
    else:
        return result[l: r]


def query_member2(stu_id):
    row_per_page = 20

    sql = "select member.stu_id, member.stu_name, belong.section_id, member.position, member.contact, member.passwd \
            from member, belong \
            where member.stu_id = belong.stu_id \
                and member.stu_id = \"{}\"  \
                order by member.stu_id".format(stu_id)
        

    result = db_execute(sql)

    return result


def update_member(sess, stu_id, name, old_passwd, new_passwd, contact, position, section):
    # pdb.set_trace()
    if sess["position"] != "chair" and (sess["position"] != "sec_head") and sess["stu_id"] != stu_id:
        return 403
    if member_exist(stu_id) == False:
        return 404
    if section != None and section_exist(section) == False:
        return 404
    if (sess["position"] == "sec_head" and get_belong(stu_id) != sess["section_id"]):
        return 403
    # if authenticate(stu_id, old_passwd)[0] != 200:
    #   return 403
    result = query_member2(stu_id)[0]
    delete_member(sess, stu_id)

    cg_passwd = False
    if name is None:
        name = result[1]
    if position is None:
        position = result[3]
    if contact is None:
        contact = result[4]
    if new_passwd is None:
        cg_passwd = True
        new_passwd = result[5]
    if section is None:
        section = result[2]

    add_member(sess, stu_id, name, new_passwd, contact, position, section, cg_passwd)
    return 200
 
    
if __name__ == "__main__":
    passwd = input()
    db = MySQLdb.connect(
        host='localhost',
        port=3309,
        user='root',
        passwd=passwd,
        db='random',
        charset='utf8'
    )
    
    init_db(db)
    create_member_table()
    create_belong_section()
    create_section_table()
    # add_member("chair", "1234567890", "wenchen", "3", "123456", "1123456", "member", 0)
    member_exist("1234567890")
    authenticate("1234567890", "123456")
    
    
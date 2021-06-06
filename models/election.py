from .basic_info import *
import datetime
import pdb

def create_reg_enable_table():
    try:
        sql = "create table reg_enable ( \
            enable int not null,  \
            primary key (enable));"
        _ = db_execute(sql)
        

        sql = "insert into reg_enable values (\"0\");"
        _ = db_execute(sql)
        
    except:
        pass

def create_cand_table():
    try:
        sql = "create table cand_prof ( \
            stu_id  int   not null, \
            stu_name varchar(128), \
            grade int, \
            contact varchar(512), \
            brief varchar(1024), \
            attachment varchar(1024), \
            primary key (stu_id)  \
        );"
        _ = db_execute(sql)
        
    except:
        pass

def create_app_table():
    try:
        sql = "create table application ( \
            stu_id int not null,   \
            section_id int not null, \
            primary key (stu_id, section_id) \
        );"
        _ = db_execute(sql)
        
    except:
        pass

def create_assign():
    try:
        sql = "create table assign ( \
            stu_id int not null,   \
            section_id int, \
        );"
        _ = db_execute(sql)
        
    except:
        pass

def create_evaluate():
    try:
        sql = "create table evaluate ( \
            judge_id int not null,   \
            stu_id int not null, \
            score int, \
            review varchar(1024), \
            rv_time varchar(1024), \
            primary key (judge_id, stu_id) \
        );"
        _ = db_execute(sql)
        
    except:
        pass

def query_reg_enable():
    sql = "select * from reg_enable;"
    print(1234)
    result = db_execute(sql)
    print(12345)
    return result[0][0] == 1

def modify_reg_enable(sess, value):
    if sess["position"] != "chair":
        return 403
    sql = "update reg_enable \
            set enable = \"{}\"".format(value)
    _ = db_execute(sql)
    
    return 200

def cand_exist(stu_id):
    sql = "select stu_id from cand_prof where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)
    return result != None

def create_candidate_profile(name, stu_id, grade, contact, applications, brief, attachment):
    if cand_exist(stu_id):
        sql = "delete from cand_prof where stu_id = \"{}\";".format(stu_id)
        _ = db_execute(sql)
        
        sql = "delete from application where stu_id = \"{}\";".format(stu_id)
        _ = db_execute(sql)
        

    sql = "insert into cand_prof \
        values (\"{}\", \"{}\",  \"{}\", \"{}\", \"{}\", \"{}\");".format(stu_id, name, grade, contact, brief, attachment)

    db_execute(sql)
    

    for application in applications:
        sql = "insert into application \
            values (\"{}\", \"{}\");".format(stu_id, application)
        db_execute(sql)
        

    return 200

def get_application(stu_id):
    sql = "select stu_id, section_id from application where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)
    return result

def get_admission(stu_id):
    sql = "select assign.section_id from assign where  assign.stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)
    return result


def query_cand_list(sess, section_id, name, page):
    row_per_page = 20
    if (sess["position"] != "sec_head") and (sess["position"] != "chair"):
        return 403
    if page is None:
        page = 1
        row_per_page = INF


    if section_id == -1 and name == "None":
        sql = "select cand_prof.stu_id, stu_name, grade, contact, student_avg.avg_score from (select stu_id, avg(score) as avg_score \
from evaluate    \
group by stu_id) as student_avg right join cand_prof on student_avg.stu_id = cand_prof.stu_id;"
        result = db_execute(sql)
    elif section_id == -1:
        sql = "select cand_prof.stu_id, stu_name, grade, contact, student_avg.avg_score from (select stu_id, avg(score) as avg_score \
from evaluate   \
group by stu_id) as student_avg right join cand_prof on student_avg.stu_id = cand_prof.stu_id \
                where stu_name = \"{}\";".format(name)
        result = db_execute(sql)
    else:
        sql = "select cand_prof.stu_id, stu_name, grade, contact, student_avg.avg_score from (select stu_id, avg(score) as avg_score \
from evaluate    \
group by stu_id) as student_avg right join cand_prof on student_avg.stu_id = cand_prof.stu_id;"
        result = db_execute(sql)

    ret = []
    if result is None:
        return []
    for i, row in enumerate(result):
        cur_ret = [row[0], row[1], row[2], row[3]]
        applicats = get_application(row[0])[:, 1]
        admitted = get_admission(row[0])
        if admitted != None:
            admitted = admitted[:, 0]
        else:
            admitted = []
        if section_id != -1 and section_id not in applicats:
            continue
        cur_ret.append(applicats)
        cur_ret.append(admitted)
        cur_ret.append(row[4])
        ret.append(cur_ret)

    if len(ret) <= row_per_page * (page - 1):
        return 200, []
    else:
        ret = ret[row_per_page * (page - 1): min(len(result), row_per_page * page)]

        return 200, ret
        


def query_cand_info(sess, stu_id):
    if sess["position"] != "chair" and (sess["position"] != "sec_head"):
        return 403
    if cand_exist(stu_id) is None:
        return 404
    sql = "select * from cand_prof \
        where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)
    application = get_application(stu_id)[:, 1]

    if sess["position"] == "sec_head":
        if application is None or int(sess["section_id"]) not in application:
            return 403

    sql = "select section_id from assign where stu_id = \"{}\";".format(stu_id)
    sec_result = db_execute(sql)
    
    return 200, result[0][1], result[0][2], result[0][3], application, result[0][4], result[0][5], [] if sec_result is None else sec_result[:, 0]

def evaluate(sess, stu_id, score, review):
    if sess["position"] != "chair" and (sess["position"] != "sec_head"):
        return 403
    if cand_exist(stu_id) is None:
        return 404
    
    if sess["position"] == "sec_head":
        application = get_application(stu_id)[:, 1]
        if application is None or int(sess["section_id"]) not in application:
            return 403
    
    sql = "insert into evaluate values (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\") \
        on duplicate key update score = \"{}\", review = \"{}\", rv_time = \"{}\"".format(
            sess["stu_id"], stu_id,
            score, review, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
            score, review, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
    _ = db_execute(sql)
    

    sql = "select avg(score) from evaluate where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)[0][0]

    return 200, result

def get_evaluate(sess, stu_id):
    if sess["position"] != "chair" and (sess["position"] != "sec_head"):
        return 403
    if cand_exist(stu_id) is None:
        return 404
    
    if sess["position"] == "sec_head":
        application = get_application(stu_id)[:, 1]
        if application is None or int(sess["section_id"]) not in application:
            return 403
    
    sql = "select member.stu_id, stu_name, section_id, rv_time, review, score \
        from member, evaluate, belong \
        where member.stu_id = evaluate.judge_id and evaluate.judge_id = belong.stu_id and evaluate.stu_id = \"{}\";".format(stu_id)

    result = db_execute(sql)
    return 200, [] if result is None else result

def admission(sess, stu_id):
    # pdb.set_trace()
    if (sess["position"] != "sec_head"):
        return 403
    if cand_exist(stu_id) is None:
        return 404
    
    if sess["position"] == "sec_head":
        application = get_application(stu_id)[:, 1]
        if application is None or int(sess["section_id"]) not in application:
            return 403

    sql = "select * from assign where section_id = \"{}\" and stu_id = \"{}\";".format(sess["section_id"], stu_id)
    result = db_execute(sql)
    if result is not None:
        return 403

    sql = "select as_count.section_id from (select section_id, count(*) as cnt from assign group by section_id) as as_count right join section on section.section_id = as_count.section_id where (as_count.cnt is NULL or as_count.cnt < section.member_limit) and section.section_id = \"{}\";".format(int(sess["section_id"]))
    result = db_execute(sql)
    if result is None:
        return 403

    else:
        # import pdb
        #pdb.set_trace()
        sql = "insert into assign values (\"{}\", \"{}\");".format(stu_id, sess["section_id"])
        _ = db_execute(sql)

        sql = "select section_id from assign where stu_id = \"{}\";".format(stu_id)
        result = db_execute(sql)
        
        return 200, result[:, 0]



    
def admission_cancel(sess, stu_id):
    # pdb.set_trace()
    if (sess["position"] != "sec_head"):
        return 403
    if cand_exist(stu_id) is None:
        return 404
    
    if sess["position"] == "sec_head":
        application = get_application(stu_id)[:, 1]
        if application is None or int(sess["section_id"]) not in application:
            return 403
    
    sql = "delete from assign where stu_id = \"{}\" and section_id = \"{}\"".format(stu_id, sess["section_id"])
    
    _ = db_execute(sql)

    sql = "select section_id from assign where stu_id = \"{}\";".format(stu_id)
    result = db_execute(sql)
    
    return 200, [] if result is None else result[:, 0]

def validate(sess):
    # import pdb
    # pdb.set_trace()
    if (sess["position"] != "sec_head") and (sess["position"] != "chair"):
        return 403
    flag = True
    sql = "select as_count.stu_id from (select stu_id, count(*) from assign group by stu_id) as as_count(stu_id, cnt) where as_count.cnt > 1;"
    result = db_execute(sql)
    if result != None:
        return 200, False
    
    sql = "select as_count.section_id from (select section_id, count(*) from assign group by section_id) as as_count(section_id, cnt), section where section.section_id = as_count.section_id and as_count.cnt < section.member_limit;"
    if result != None:
        return 200, False

    return 200, True


def admit_finish(sess):
    # pdb.set_trace()
    if sess["position"] != "chair":
        return 403

    _ = db_execute("begin;")

    sql = "select cand_prof.stu_id, cand_prof.stu_name, cand_prof.contact, assign.section_id from cand_prof, assign where cand_prof.stu_id = assign.stu_id;"
    result = db_execute(sql)

    

    flag = True

    for record in result:
        stu_id, stu_name, contact, section_id = record
        add_member(sess, stu_id, stu_name, "12345678", contact, "member", section_id)

    sql = "delete from cand_prof; delete from application; delete from assign; delete from evaluate;"
    _ = db_execute(sql)
    _ = db_execute("commit;")

    return 200

def clean_all(sess):
    if sess["position"] != "chair":
        return 403
    sql = "delete from cand_prof; delete from application; delete from assign; delete from evaluate;"
    result = db_execute(sql)
    
    return 200

def create_all():
    create_reg_enable_table()
    create_member_table()
    create_belong_section()
    create_section_table()
    create_assign()
    create_cand_table()
    create_app_table()
    create_evaluate()
    db_init()

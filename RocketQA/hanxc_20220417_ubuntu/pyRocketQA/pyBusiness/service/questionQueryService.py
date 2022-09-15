import requests
import json
import pandas as pd
import faiss
import rocketqa
import os
import subprocess
import psutil
import time
from commons import db_util
from commons import common_const



from psycopg2.extras import execute_values


def getQA(sentence: str, df):
    sentence = sentence.replace(";", "；")
    sentence = sentence.replace("\\", "\\\\")
    sentence = sentence.replace("'", "''")
    sentence = sentence.replace("\"", "\\\"")
    result_str = query(sentence, df)

    result = {}
    result['count'] = common_const.TOPK
    result['data'] = result_str
    return result


def saveVote(conn, id, upNum, downNum):
    """

    :param id:
    :param is_up:
    :param num:
    :return:
    """
    try:
        db_util.update_data(conn, id, upNum, downNum)
    except Exception as e:
        raise e

def getFilePath(file_name):
    commons_dir = os.path.dirname(__file__)
    src_dir = os.path.dirname(commons_dir)
    pyscript_dir = os.path.dirname(src_dir)
    return os.path.join(pyscript_dir, file_name)


def saveFileToDB(file, conn):
    # 读取EXCEL文件
    ef = pd.read_excel(file, sheet_name='Sheet1', engine='openpyxl')
    # 链接Postgres数据库
    cur = conn.cursor()

    # 删除表的所有数据
    delete_SQL = "DELETE FROM m_info;"
    cur.execute(delete_SQL)

    # 插入数据的SQL文
    insert_SQL = "INSERT INTO m_info(id, kind, question, answer, qaclass, qaurl, creatdate, numupvote, numdownvote) VALUES %s ;"

    # 统计数据行数
    nbs = 0
    # 插入用的list
    params = []

    # 数据行数循环
    for row in ef.values:
        # 统计行数
        nbs += 1
        # 把一行数据的各个列组织成变量
        cols = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

        # 变量加入list
        params.append(cols)

    # 批量插入
    ret = execute_values(cur, insert_SQL, params, page_size=nbs)

    # 提交
    conn.commit()

    print("data is imported!")
    # # 关闭
    # cur.close()

    try:

        db_util.update_m_sys(conn, "index_status", "1")  # 开始执行，即执行中
        callCreateIndexData()
    except:
        db_util.update_m_sys(conn, "index_status", "2")  # 异常

    # 关闭
    cur.close()

def callCreateIndexData():
    cmd = getFilePath("createIndexData.py")

    # Windows
    if os.name == 'nt':
        p = subprocess.Popen("python " + cmd)
    # Ubuntu
    else:
        p = subprocess.Popen("exec python3 " + cmd, shell=True)

    # saveIndexFromDB(conn)



def query(query, df):
    """

    :param query:问题
    :return:查询结果
    """
    SERVICE_ADD = 'http://' + common_const.SERVICE_HOST + ":" + common_const.SERVICE_PORT + common_const.SERVICE_SUB_ADDRESS
    topk = common_const.TOPK

    if query.strip() == '':
        return

    input_data = {}
    input_data['query'] = query
    input_data['topk'] = topk

    result = requests.post(SERVICE_ADD, json=input_data)
    res_json = json.loads(result.text)
    answer = res_json["answer"]
    if answer is None or len(answer) == 0:
        return res_json
    for i in range(len(answer)):
        id = int(answer[i]['id'])
        df_filter = df[(df["id"] == int(id))]
        answer[i]['question'] = str(df_filter.iloc[0]["question"])
        answer[i]['kind'] = str(df_filter.iloc[0]["kind"])
        answer[i]['answer'] = str(df_filter.iloc[0]["answer"])
        answer[i]['qaurl'] = str(df_filter.iloc[0]["qaurl"])
        answer[i]['qaclass'] = str(df_filter.iloc[0]["qaclass"])
        answer[i]['creatdate'] = str(df_filter.iloc[0]["creatdate"])
        answer[i]['numupvote'] = str(df_filter.iloc[0]["numupvote"])
        answer[i]['numdownvote'] = str(df_filter.iloc[0]["numdownvote"])
    return res_json


def restartService(CONN):

    process_id = db_util.get_m_sys_data(CONN, "pid")

    if process_id != "0":
        try:
            # 查找到pid，并kill掉
            pro = psutil.Process(int(process_id))
            pro.terminate()
            db_util.update_m_sys(CONN, "pid", "0")
        except:
            pass

    cmd = getFilePath("rocketqa_service_start.py")

    # Windows
    if os.name == 'nt':
        p = subprocess.Popen("python " + cmd)
    # Ubuntu
    else:
        p = subprocess.Popen("exec python3 " + cmd, shell=True)

    # 等待，直到服务重启完成后
    df = db_util.get_data(CONN, common_const.TABLE_NAME)
    for i in range(60):
        try:
            query("aaa", df)

            break
        except Exception as e:
            time.sleep(2)
            if str(e).find("NewConnectionError") > 0:
                pass
            else:
                break

    db_util.update_m_sys(CONN, "pid", str(p.pid))



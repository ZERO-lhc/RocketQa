import psycopg2
import pandas as pd
from commons import common_const



def connect():
    """
    DB连接
    :return:
    """
    # env_file_util.load_ebv_file()
    conn_string = "host=" + common_const.DB_SERVER_HOST + " port=" + common_const.DB_SERVER_PORT \
                  + " dbname=" + common_const.DB_DATABASE_NAME \
                  + " user=" + common_const.DB_USER \
                  + " password=" + common_const.DB_PW
    con = psycopg2.connect(conn_string)

    return con


def get_data(con, table_nane):
    """
    根据表名，取得数据
    :param con:
    :return:
    """
    sql = "SELECT * FROM " + table_nane

    df = pd.read_sql(sql, con)
    return df

def get_m_sys_data(con, key1):
    """
    根据表名，取得数据
    :param con:
    :return:
    """
    sql = "SELECT value1 FROM m_sys where key1 = '" + key1 + "'"

    df = pd.read_sql(sql, con)

    for index, row in df.iterrows():
        value = str(row['value1'])

    return value

def update_data(conn, id, upNum, downNum):
    """
    点赞处理
    :param conn:
    :param id:
    :param upNum:
    :param downNum:
    :return:
    """
    sql = "update " + common_const.TABLE_NAME + " set numupvote= numupvote +" + upNum + " ,numdownvote= numdownvote+" + downNum + " where id=" + id

    try:
        curs = conn.cursor()
        # SQL文を実行
        curs.execute(sql)
        conn.commit()
    except Exception as e:
        raise e
    finally:
        try:
            curs.close()
        except:
            pass

def update_m_sys(conn, key1, value1):

    sql = "update m_sys set value1=" + value1 + " where key1='" + key1 + "'"
    try:
        curs = conn.cursor()
        # SQL文を実行
        curs.execute(sql)
        conn.commit()
    except Exception as e:
        raise e
    finally:
        try:
            curs.close()
        except:
            pass
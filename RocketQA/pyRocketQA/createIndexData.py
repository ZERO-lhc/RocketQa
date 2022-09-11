import faiss
import rocketqa

import os
from commons import db_util
from commons import common_const

dual_encoder=None

def build_index(encoder_conf, index_file_name, title_list, para_list, conn):
    global dual_encoder
    if dual_encoder is None:
        dual_encoder = rocketqa.load_model(**encoder_conf)
    para_embs = dual_encoder.encode_para(para=para_list, title=title_list)

    indexer = faiss.IndexFlatIP(768)
    indexer.add(para_embs.astype('float32'))
    faiss.write_index(indexer, index_file_name)

    db_util.update_m_sys(conn, "index_status", "0")  # 执行完成，设置为初始值

def saveIndexFromDB():
    conn = db_util.connect()
    commons_dir = os.path.dirname(__file__)
    src_dir = os.path.dirname(commons_dir)
    pyscript_dir = os.path.dirname(src_dir)

    language = common_const.LANGUAGE

    if os.name == 'nt':
        index_file = os.path.join(commons_dir, common_const.SERVICE_NAME)
    else:
        index_file = os.path.join(src_dir, common_const.SERVICE_NAME)


    if language == 'zh':
        model = 'zh_dureader_de'
    elif language == 'en':
        model = 'v1_marco_de'
    else:
        print("illegal language, only [zh] and [en] is supported")
        exit()

    para_list = []
    title_list = []

    # m_info表取得数据
    df = db_util.get_data(conn, common_const.TABLE_NAME)

    for index, row in df.iterrows():
        title_list.append(str(row['question']))
        para_list.append(str(row['answer']))

    de_conf = {
        "model": model,
        "use_cuda": False
    }

    build_index(de_conf, index_file, title_list, para_list, conn)

if __name__ == "__main__":
    saveIndexFromDB()
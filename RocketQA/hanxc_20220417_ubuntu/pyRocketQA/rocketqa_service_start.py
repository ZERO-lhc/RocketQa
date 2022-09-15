import imp
import sys
import json
from tracemalloc import start
import faiss
import os
import time
from tornado import web
from tornado import ioloop

from commons import db_util
from commons import common_const


import rocketqa


class FaissTool():
    """
    Faiss index tools
    """

    def __init__(self, index_filename, df):
        self.engine = faiss.read_index(index_filename)
        self.id2text = []

        for index, row in df.iterrows():
            id2text_sub = []
            id2text_sub.append(str(row['id']))
            id2text_sub.append(str(row['question']))
            id2text_sub.append(str(row['answer']))
            self.id2text.append(id2text_sub)
            """
            self.id2text.append(str(row['question']).replace('\t', '') + '\t' + str(row['kind'])
                                + '\t' + str(row['answer']).replace('\t', '')
                                + '\t' + str(row['qaurl'])
                                + '\t' + str(row['qaclass'])
                                + '\t' + str(row['creatdate'])
                                + '\t' + str(row['numupvote'])
                                + '\t' + str(row['numdownvote'])
                                + '\t' + str(row['id']))
            """

    def search(self, q_embs, topk=common_const.TOPK):
        res_dist, res_pid = self.engine.search(q_embs, topk)
        result_list = []

        for i in range(topk):
            result_list.append(self.id2text[res_pid[0][i]])
        return result_list


class RocketQAServer(web.RequestHandler):
    def runtime(start,end):
        return start - end


    def __init__(self, application, request, **kwargs):
        web.RequestHandler.__init__(self, application, request)
        self._faiss_tool = kwargs["faiss_tool"]
        self._dual_encoder = kwargs["dual_encoder"]
        self._cross_encoder = kwargs["cross_encoder"]

    def get(self):
        """
        Get request
        """

    def post(self):
        input_request = self.request.body
        output = {}
        output['error_code'] = 0
        output['error_message'] = ''
        output['answer'] = []
        if input_request is None:
            output['error_code'] = 1
            output['error_message'] = "Input is empty"
            self.write(json.dumps(output))
            return

        try:
            input_data = json.loads(input_request)
        except:
            output['error_code'] = 2
            output['error_message'] = "Load input request error"
            self.write(json.dumps(output))
            return

        if "query" not in input_data:
            output['error_code'] = 3
            output['error_message'] = "[Query] is missing"
            self.write(json.dumps(output))
            return

        query = input_data['query']
        topk = common_const.TOPK
        if "topk" in input_data:
            topk = input_data['topk']

        # encode query
        q_embs = self._dual_encoder.encode_query(query=[query])

        # search with faiss
        start = time.time()        
        search_result = self._faiss_tool.search(q_embs, topk)
        end = time.time()
        print('检索时间为：{}',format(end-start))

        ids = []
        queries = []
        questions = []
        answers = []
        """
        kinds = []
        qaurls = []
        qaclasss = []
        creatdates = []
        numupvotes = []
        numdownvotes = []
        """

        for t_p in search_result:
            # no question has been found
            if t_p is None or len(str(t_p).strip()) == 0:
                continue
            # format error
            queries.append(query)
            id = t_p[0]
            question = t_p[1]
            answer = t_p[2]
            questions.append(question)
            answers.append(answer)
            ids.append(id)
        ranking_score = self._cross_encoder.matching(query=queries, para=answers, title=questions)

        final_result = {}
        for i in range(len(answers)):
            final_result[str(ids[i]) + '\t' + query + '\t' + questions[i] + '\t' +  answers[i]] = ranking_score[i]
        sort_res = sorted(final_result.items(), key=lambda a: a[1], reverse=True)

        for qtp, score in sort_res:
            if float(score) < float(common_const.PROBABILITY):
                break
            one_answer = {}
            one_answer['probability'] = score
            relust_t_p = qtp.split('\t')
            one_answer['id'] = relust_t_p[0]
            one_answer['question'] = ""
            one_answer['kind'] = ""
            one_answer['answer'] = ""
            one_answer['qaurl'] = ""
            one_answer['qaclass'] = ""
            one_answer['creatdate'] = ""
            one_answer['numupvote'] = ""
            one_answer['numdownvote'] = ""

            output['answer'].append(one_answer)

        result_str = json.dumps(output, ensure_ascii=False)
        self.write(result_str)


def create_rocketqa_app(sub_address, rocketqa_server, index_file, de_model, ce_model, df):
    """
    Create RocketQA server application
    """

    de_conf = {
        "model": de_model,
        "use_cuda": False,
        "device_id": 0,
        "batch_size": 32
    }
    ce_conf = {
        "model": ce_model,
        "use_cuda": False,
        "device_id": 0,
        "batch_size": 32
    }

    dual_encoder = rocketqa.load_model(**de_conf)
    cross_encoder = rocketqa.load_model(**ce_conf)

    faiss_tool = FaissTool(index_file, df)
    print('Load index done')

    return web.Application([(sub_address, rocketqa_server, \
                             dict(faiss_tool=faiss_tool, \
                                  dual_encoder=dual_encoder, \
                                  cross_encoder=cross_encoder))])


def create_rocketqa_app(sub_address, rocketqa_server, index_file, de_model, ce_model, df):
    """
    Create RocketQA server application
    """

    de_conf = {
        "model": de_model,
        "use_cuda": False,
        "device_id": 0,
        "batch_size": 32
    }
    ce_conf = {
        "model": ce_model,
        "use_cuda": False,
        "device_id": 0,
        "batch_size": 32
    }

    dual_encoder = rocketqa.load_model(**de_conf)
    cross_encoder = rocketqa.load_model(**ce_conf)

    faiss_tool = FaissTool(index_file, df)
    print('Load index done')

    return web.Application([(sub_address, rocketqa_server, \
                             dict(faiss_tool=faiss_tool, \
                                  dual_encoder=dual_encoder, \
                                  cross_encoder=cross_encoder))])

from ..service import questionQueryService
import json


def queryList(sentence: str, df):
    return json.dumps(questionQueryService.getQA(sentence, df))


def saveVote(conn, id, upNum, downNum):
    questionQueryService.saveVote(conn, id, upNum, downNum)

def saveFileToDB(conn, file):
    questionQueryService.saveFileToDB(file, conn)

def restartService(conn):
    questionQueryService.restartService(conn)
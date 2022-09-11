from django.shortcuts import HttpResponse
from pyBusiness.controller import questionController
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from commons import db_util
#from commons import env_file_util
from commons import common_const




#env_file_util.load_ebv_file()
CONN = db_util.connect()

def canSearch():
    retVal = db_util.get_m_sys_data(CONN, "index_status")
    if retVal == "0":
        return True
    return False

def canUpload():
    if db_util.get_m_sys_data(CONN, "index_status") != "1":
        return True
    return False

def QuestionQueryService(request):
    global CONN

    if not canSearch():
        return HttpResponse(status=500)

    df = db_util.get_data(CONN, common_const.TABLE_NAME)
    if request.method == 'GET':
        page = request.GET.get('page', None)
        sentence = request.GET.get('sentence')
        res_jsons = questionController.queryList(sentence, df)
        response = HttpResponse(res_jsons)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    elif request.method == 'POST':
        # page = request.POST.get('page',None)
        print(request.POST['sentence'])
        res_jsons = questionController.queryList(request.POST['sentence'])
        return HttpResponse(res_jsons)
    else:
        return 'Use GET or POST to request this API!'


def VoteService(request):
    global CONN
    id = request.GET['questionId']
    upNum = request.GET['numUpvote']
    downNum = request.GET['numDownvote']
    questionController.saveVote(CONN, id, upNum, downNum)

    return HttpResponse("vote success")


def SaveIndexFile(request):
    if not canUpload():
        return HttpResponse(status=500)

    file = request.FILES['indexFile']
    path = default_storage.save("temp/temp.xlsx", ContentFile(file.read()))
    questionController.saveFileToDB(CONN, path)

    return HttpResponse("save success")

def RestartService(request):
    global CONN
    if not canSearch():
        return HttpResponse(status=500)

    questionController.restartService(CONN)

    return HttpResponse("restart success")

def KeepConnection(request):
    return HttpResponse("keep success")
#coding:utf-8

from flask_restful import Resource,reqparse,inputs
from flask import jsonify,g
from . import api
from ..common.alopex_auth_sdk import need_login
from ..common.ApiResponse import ApiResponse,ResposeStatus
from ..domain.repo import getRepoList,addToSearch,delFromSearch,getRepo,hook,getHistory
from ..tasks.syncFromGitlab import gitlabSync
from ..tasks.syncToSearchCode import searchSync
from ..tasks.syncTasks import syncSearchCodeStatus
def get_args():
    rp = reqparse.RequestParser()
    rp.add_argument('offset',type=int,default=0)
    rp.add_argument('limit',type=int,default=20)
    rp.add_argument('keyword',type=unicode,required=False)
    rp.add_argument('id',type=unicode,default='')
    return rp.parse_args()

def post_args():
    rp =reqparse.RequestParser()
    rp.add_argument('id',type=unicode,required=True)
    return rp.parse_args()

class repoList(Resource):
    def get(self):
        args=get_args()
        return ApiResponse(getRepoList(keyword=args.keyword,offset=args.offset,limit=args.limit))

class syncGit(Resource):
    def get(self):
        gitlabSync()
        return ApiResponse()

class syncSearchCode(Resource):
    def get(self):
        searchSync()
        return ApiResponse()


class codeSync(Resource):
    def post(self,id):
        res = addToSearch(id)
        if res['sucessful']:
            status = ResposeStatus.Success
        else:
            status = ResposeStatus.Fail
        return ApiResponse(res,status)
    def delete(self,id):
        res = delFromSearch(id)
        if res['sucessful']:
            status = ResposeStatus.Success
        else:
            status = ResposeStatus.Fail
        return ApiResponse(res,status)

class repo(Resource):
    def get(self,id):
        return ApiResponse(getRepo(id))

class demo(Resource):
    def get(self):
        return ApiResponse(syncSearchCodeStatus())

class gitHook(Resource):
    def post(self):
        return ApiResponse(hook())

class historyList(Resource):
    def get(self):
        args=get_args()
        return ApiResponse(getHistory(keyword=args.keyword,offset=args.offset,limit=args.limit))

class test(Resource):
    def get(self):
        return ApiResponse(add.delay())


api.add_resource(syncGit, '/gitsync')
api.add_resource(syncSearchCode,'/searchsync')
api.add_resource(repoList,'/repolist')
api.add_resource(repo,'/repo/<id>')
api.add_resource(codeSync, '/cs/<id>')
api.add_resource(gitHook, '/githook')
api.add_resource(historyList, '/historylist')
api.add_resource(demo, '/demo')
api.add_resource(test,'/demo2')
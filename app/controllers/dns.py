from flask_restful import Resource,reqparse,inputs
from flask import jsonify,g
import json,requests
from . import api
from ..common.DNSManage import getlist,getDetail,Createrecord,Updaterecord,Deleterecord
from ..common.alopex_auth_sdk import need_login,need_login2
from ..common.ApiResponse import ApiResponse
import app
from app import logger



def post_args():
    rp=reqparse.RequestParser()
    rp.add_argument('domain',type=unicode,default='apitops.com')
    rp.add_argument('value',type=unicode,required=True, nullable=False)
    rp.add_argument('type',default='A')
    return rp.parse_args()

def get_args():
    rp=reqparse.RequestParser()
    rp.add_argument('domain',type=unicode,default='apitops.com')
    rp.add_argument('offset',type=int,default=0)
    rp.add_argument('limit',type=int,default=20)
    rp.add_argument('keyword',type=unicode,required=False)
    rp.add_argument('type',default='A')
    return rp.parse_args()


class Dnslist(Resource):
    def get(self):
        args=get_args()
        return {'data':getlist(args.domain,keyword=args.keyword,offset=args.offset,limit=args.limit,type=args.type)}

class Dns(Resource):
    def get(self,query):
        args=get_args()
        #return {'data':getDetail(query,args.domain)}
        return ApiResponse(getDetail(query,args.type,args.domain))
    @need_login2(roles=['admin'])
    def post(self,query,):
        args=post_args()
        #return {'data':Createrecord(query,args.value,args.domain)}
        res,status = Createrecord(query,args.value,args.domain,type=args.type)
        return ApiResponse(res,status)

    @need_login2(roles=['admin'])
    def put(self,query):
        args=post_args()
        res,status = Updaterecord(query,args.value,args.domain,type=args.type)
        return ApiResponse(res,status)

    @need_login2(roles=['admin'])
    def delete(self,query):
        args=get_args()
        return {'data':Deleterecord(query,args.domain,type=args.type)}
api.add_resource(Dnslist,'/dnslist')
api.add_resource(Dns,'/dns/<query>')

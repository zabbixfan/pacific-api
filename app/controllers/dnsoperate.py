from flask_restful import Resource,reqparse,inputs
import json,requests
from . import api
from ..common.DNSManage import getlist,getDetail,Createrecord,Updaterecord,Deleterecord
from ..common.alopex_auth_sdk import need_login
from flask import request
import logging
dnsmanager='http://192.168.6.120:5000/dns'

def post_args():
    rp=reqparse.RequestParser()
    rp.add_argument('domain',type=unicode,default='apitops.com')
    #rp.add_argument('devip',type=unicode,required=False, nullable=False)
    return rp.parse_args()

class Configdns(Resource):
    @need_login()
    def post(self,query):
        message=Resolve("post",query)
        for i in message:
            print i
            if not i[0]['message'].endswith("success"):
                return {"message": "please failed,check log"}, 404
        return {"message": "ok"}, 200
    @need_login()
    def delete(self,query):
        message=Resolve("delete",query)
        for i in message:
            print i
            if not i['Message'].endswith("success"):
                return {"message": "please failed,check log"}, 404
        return {"message": "ok"}, 200

def Resolve(action,query):
    args = post_args()
    ips = {
        'dev': '192.168.100.60',
        'test': '192.168.100.54',
        'beta': '192.168.255.65',
        'v5': '120.55.248.200'
    }
    result = []
    for k, v in ips.items():
        record=query

        if k !='v5':
            record='{}.{}'.format(record,k)
        if action == "delete":
            print 'begin to delete resolve {}.{} ,env {}'.format(record, args.domain, k)
            res=Deleterecord(record,args.domain)
        if action == "post":
            print 'begin to create resolve {}.{} ,env {}'.format(record, args.domain, k)
            res=Createrecord(record,v,args.domain)
        #     r = requests.post(url, data=payload)
        # res= r.json()
        result.append(res)
    return result
api.add_resource(Configdns,'/dnsbatch/<query>')
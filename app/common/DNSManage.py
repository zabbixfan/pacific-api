from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import DeleteDomainRecordRequest
from .Aliyunsdk import LoadSDK
from flask import g
import re
from ..common.ApiResponse import ResposeStatus
from ..common.string_helper import reg_parser
from config import Config
from app import logger

def getlist(domainname=Config.DOMAIN,type=None,keyword=None,offset=0,limit=10):
    '''
    Get All DNS RECORD
    :return:
    '''
    rel = []
    currentIndex = 1
    totalPage = 1
    pageSize = 500
    while currentIndex <= totalPage:
        req = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        req.set_PageSize(pageSize)
        req.set_PageNumber(currentIndex)
        req.set_DomainName(domainname)
        try:
            res = LoadSDK(req, "cn-hangzhou")
        except Exception as e:
            break
        currentIndex += 1
        #print json.dumps(res,indent=2)
        # print "total,{}".format(res["TotalRecordCount"])
        totalPage = res.get("TotalCount") / pageSize if res.get(
            "TotalCount") % pageSize == 0 else res.get(
            "TotalCount") / pageSize + 1
        rel += res.get("DomainRecords").get("Record")
    TotalCount=res.get("TotalCount")
    records=[]
    for res in rel:
        if type is None or res['Type'] == type:
            record = {
                "Record": res["RR"],
                "Value": res["Value"],
                "RecordId": res["RecordId"],
                "Type": res["Type"],
                "DomainName": res["DomainName"]
            }
            if keyword != None and (record['Record'].find(keyword) > -1 or record['Value'].find(keyword) > -1):
                records.append(record)
            if keyword == None:
                records.append(record)
        # elif res['Type'] == type:
        #     record = {
        #         "Record": res["RR"],
        #         "Value": res["Value"],
        #         "RecordId": res["RecordId"],
        #         "Type": res["Type"],
        #         "DomainName": res["DomainName"]
        #     }

    if limit==-1 or limit==0:
        records = records[offset:]
    else:
        records = records[offset:offset+limit]
    return {'Datalist':records,'TotalCount':TotalCount,"Start":offset,"Limit":limit}
def getDetail(query,type="A",domainname=Config.DOMAIN):
    for res in getlist(domainname,type,limit=-1)['Datalist']:
        if 'Record' in res.keys() and res['Record']==query:
            return [res]
    return []
def Createrecord(query,value,domainname=Config.DOMAIN,type="A"):
    # valuePattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    # queryPattern = re.compile(r'^[\d\w\.]+$')
    if type == "A":
        if not reg_parser(query,'record') or not reg_parser(value,'value') :
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
    elif type == "CNAME":
        if not reg_parser(query,'record'):
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
        if not reg_parser(value, 'value') and not reg_parser(value, 'record'):
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
    res=getDetail(query,type,domainname)
    if res == []:
        add_r=AddDomainRecordRequest.AddDomainRecordRequest()
        add_r.set_DomainName(domainname)
        add_r.set_RR(query)
        add_r.set_Type(type)
        add_r.set_Value(value)
        try:
            res=LoadSDK(add_r)
        except Exception,e:
            logger().info(e.message)
        print g.__dict__.keys()
        res['message']='Domain {}.{} value {} type {} create success'.format(query,domainname,value,type)
        if 'user' in g.__dict__.keys():
            logger().info('{} by {}'.format(res['message'],g.user['loginName']))
        else:
            logger().info('{} by workflow'.format(res['message']))

    else:
        logger().info('create {}.{} value {} type {} failed by {}'.format(query,domainname,value,type,g.user['loginName']))
        return [{'message':'DNS record {}.{} {} already exist'.format(query,domainname,value)},ResposeStatus.Fail]
    return [res,ResposeStatus.Success]
def Updaterecord(query,value,domainname=Config.DOMAIN,type="A"):
    if type == "A":
        if not reg_parser(query,'record') or not reg_parser(value,'value') :
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
    elif type == "CNAME":
        if not reg_parser(query,'record'):
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
        if not reg_parser(value, 'value') and not reg_parser(value, 'record'):
            return [{'message': 'invalid value or record '}, ResposeStatus.Fail]
    res=getDetail(query,type,domainname)
    content = 'update {}.{} value {} type {}'.format(query,domainname,value,type)
    if res == []:
        logger().info('{} failed because value don\' exist by {}'.format(content,g.user['loginName']))
        return [{'message':'Domain {}.{} value {} don\'t exist'.format(query,domainname,value)},ResposeStatus.Fail]
    elif res[0]['Record']==query and res[0]['Value']==value:
        logger().info('{} failed because value already exist by {}'.format(content,g.user['loginName']))
        return [{'message':'Domain {}.{} value {} already exist'.format(query,domainname,value)},ResposeStatus.Fail]
    else:
        mod_r=UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        mod_r.set_RecordId(res[0]['RecordId'])
        mod_r.set_RR(query)
        mod_r.set_Value(value)
        mod_r.set_Type(type)
        try:
            res=LoadSDK(mod_r)
        except Exception,e:
            logger().info(e.message)
        res['message']='Domain {}.{} value {} update success'.format(query,domainname,value)

        if 'user' in g.__dict__.keys():
            logger().info('{} by {}'.format(res['message'],g.user['loginName']))
        else:
            logger().info('{} by workflow'.format(res['message']))

        #logger().info('{} success by {}'.format(content,g.user['loginName']))
        return [res,ResposeStatus.Success]
def Deleterecord(query,domainname=Config.DOMAIN,type="A"):
    res=getDetail(query,type,domainname)
    content = 'delete {}.{} type {}'.format(query, domainname, type)
    if res == []:
        logger().info('{} failed because record don\' exist by {}'.format(content,g.user['loginName']))
        return {'Message':'DNS record {}.{} don\'t exist'.format(query, domainname)}
    else:
        del_r=DeleteDomainRecordRequest.DeleteDomainRecordRequest()
        del_r.set_RecordId(res[0]['RecordId'])
        try:
            res=LoadSDK(del_r)
        except Exception,e:
            logger().info(e.message)
        logger().info('{} success by {}'.format(content,g.user['loginName']))
        res['Message'] = 'DNS record {}.{} delete success'.format(query, domainname)
        return res
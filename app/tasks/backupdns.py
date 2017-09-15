#coding: utf-8
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest
from app.common.Aliyunsdk import LoadSDK
import datetime
import re,os
from app import logger
from config import Config
import json
import time
from app import celery
def backupdnslist(domainname=Config.DOMAIN,type=None,keyword=None,offset=0,limit=10):
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
        totalPage = res.get("TotalCount") / pageSize if res.get(
            "TotalCount") % pageSize == 0 else res.get(
            "TotalCount") / pageSize + 1
        rel += res.get("DomainRecords").get("Record")
    TotalCount = res.get("TotalCount")

    return rel,TotalCount

def writeBackupToFile(domain):
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dnsbackup')
    rel,count = backupdnslist(domainname=domain)
    date = format(datetime.datetime.now(),'%Y-%m-%d')
    filename = '{}-{}-{}'.format(date,domain,count)
    file = os.path.join(dir,filename)
    with open(file,'w+') as f:
        for item in rel:
            f.write('{}\n'.format(json.dumps(item)))
def delbackup(days=5):
    backuptime = time.mktime((datetime.datetime.now() - datetime.timedelta(days=days)).timetuple())
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dnsbackup')
    for file in os.listdir(dir):
        # createtime = os.path.getctime(os.path.join('dnsbackup',i))
        createtime = os.stat(os.path.join(dir,file)).st_ctime
        if createtime < backuptime:
            logger().warn('delete dnsbackup/{}'.format(file))
            os.remove(os.path.join(dir,file))

@celery.task()
def backup():
    delbackup()
    for domain in Config.BACKUPDOMAIN:
        writeBackupToFile(domain=domain)
    return ""


if __name__ == '__main__':
    delbackup()
    for domain in Config.BACKUPDOMAIN:
        writeBackupToFile(domain=domain)
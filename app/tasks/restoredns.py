from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest
from app.tasks.backupdns import backupdnslist
import json
from app.common.Aliyunsdk import LoadSDK
from app import logger
def restore(domain,backupfile):
    dnslist = []
    with open(backupfile) as f:
        for line in f.readlines():
            dnslist.append(line.rstrip('\n'))
    current, _ = backupdnslist(domainname=domain)
    for i in dnslist:
        restore_one(json.loads(i),current,domain)

def restore_one(record,currentlist,domain):
    for c_item in currentlist:
        if record['RR'] == c_item['RR'] and record['Value'] == c_item['Value'] and record['Type'] == c_item['Type']:
            break
        if record['RR'] == c_item['RR'] and record['Value'] != c_item['Value']:
            mod_r = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
            mod_r.set_RecordId(c_item['RecordId'])
            mod_r.set_RR(record['RR'])
            mod_r.set_Value(record['Value'])
            mod_r.set_Type(record['Type'])
            try:
                res = LoadSDK(mod_r)
            except Exception, e:
                logger().info(e.message)
            print 'update {}.{} success'.format(record['RR'],domain)
            break
    else:
        add_r=AddDomainRecordRequest.AddDomainRecordRequest()
        add_r.set_DomainName(domain)
        add_r.set_RR(record['RR'])
        add_r.set_Value(record['Value'])
        add_r.set_Type(record['Type'])
        try:
            res=LoadSDK(add_r)
        except Exception,e:
            logger().info(e.message)
        print 'create {}.{} success'.format(record['RR'],domain)

if __name__ == '__main__':
    restore(domain='kingsbroker.com.cn',backupfile='dnsbackup/2017-07-11-tops001.com-169')
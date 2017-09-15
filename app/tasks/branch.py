#coding: utf-8
import requests,json
import datetime,time
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
from config import Config
token=Config.GIT_PRIVATE_TOKEN
def strtime_to_datetime(timestr, format_str="%Y-%m-%dT%H:%M:%S.%f"):
    """将字符串格式的时间 (含毫秒) 转为 datetiem 格式

    :param timestr: {str}'2016-02-25 20:21:04.242'
    :return: {datetime}2016-02-25 20:21:04.242000
    """
    local_datetime = datetime.datetime.strptime(timestr, format_str)
    return local_datetime
def strtime_to_timestamp(local_timestr):
    """将本地时间 (字符串格式，含毫秒) 转为 13 位整数的毫秒时间戳

    :param local_timestr: {str}'2016-02-25 20:21:04.242'
    :return: 1456402864242
    """
    local_datetime = strtime_to_datetime(local_timestr)
    timestamp = datetime_to_timestamp(local_datetime)
    return timestamp
def datetime_to_timestamp(datetime_obj):
    """将本地(local) datetime 格式的时间 (含毫秒) 转为毫秒时间戳

    :param datetime_obj: {datetime}2016-02-25 20:21:04.242000
    :return: 13 位的毫秒时间戳  1456402864242
    """
    local_timestamp = long(time.mktime(datetime_obj.timetuple()) + datetime_obj.microsecond)
    return local_timestamp
def time_parse(start,end):
    start = strtime_to_timestamp(str(start))
    end = strtime_to_timestamp(str(end))
    # return strtime_to_datetime(str(i['commit']['committed_date'][0:-10]),format_str='%Y-%m-%dT%H:%M:%S')
    print start,end
    return (end - start) / 86400
def gitlabSync():
    current = 1
    total = 1
    pageSize = 100
    rel = []
    while current <= total:
        url = '{}/api/v3/projects/all?per_page={}&page={}'.format(Config.GITLAB_URL,pageSize, current)
        head = {'PRIVATE-TOKEN': token}
        r = requests.get(url, headers=head)
        total = int(r.headers['X-Total-Pages'])
        current += 1
        [rel.append(res) for res in r.json()]
    return rel
    # for i in rel:
    #
    #     url = '{}/api/v3/projects/{}/repository/branches'.format(Config.GITLAB_URL, i['id'])
    #     head = {'PRIVATE-TOKEN': token}
    #     r = requests.get(url,headers=head)
    #     # branchs=[]
    #     # [branchs.append({
    #     #         'name':branch['name'],
    #     #         'commit_date':branch['commit']['committed_date']
    #     #     }) for branch in r.json()]
    #     if 'master' in [branch['name'] for branch in r.json()]:
    #         print '{} no master branch,url :{}'.format(i['name'],i['web_url'])
# gitlabSync()
# print json.dumps(r.json(),indent=4)
projects = []
starttime = datetime.datetime.now()
p = gitlabSync()

def worker(project):
    url = '{}/api/v3/projects/{}/repository/branches'.format(Config.GITLAB_URL, project['id'])
    head = {'PRIVATE-TOKEN': token}
    branchs = requests.get(url, headers=head).json()
    branchs.sort(key=lambda x:x['commit']['committed_date'])
    # print project['name']
    if len(branchs)> 0:
        if strtime_to_datetime(branchs[-1]['commit']['committed_date'][0:-10],format_str='%Y-%m-%dT%H:%M:%S') > (datetime.datetime.now()-datetime.timedelta(days=138)):
            for b in branchs:
                if b['name'] == 'master':
                    date =  time_parse(b['commit']['committed_date'][0:-6],branchs[-1]['commit']['committed_date'][0:-6])
                    projects.append({
                        'name': project['name'],
                        'date': date,
                        'start': b['commit']['committed_date'][0:-6],
                        'end': branchs[-1]['commit']['committed_date'][0:-6]
                    })
                    break
            else:
                projects.append({
                    'name': 'name',
                    'date': 'no master'
                    ''
                })
pool = ThreadPool()
pool.map(worker,p)
pool.close()
pool.join()
# for project in gitlabSync():
#     url = '{}/api/v3/projects/{}/repository/branches'.format(Config.GITLAB_URL, project['id'])
#     head = {'PRIVATE-TOKEN': token}
#     branchs = requests.get(url, headers=head).json()
#     branchs.sort(key=lambda x:x['commit']['committed_date'])
#     # print project['name']
#     if len(branchs)> 0:
#         if strtime_to_datetime(branchs[-1]['commit']['committed_date'][0:-10],format_str='%Y-%m-%dT%H:%M:%S') > (datetime.datetime.now()-datetime.timedelta(days=138)):
#
#             for b in branchs:
#                 if b['name'] == 'master':
#                     date =  time_parse(b['commit']['committed_date'][0:-6],branchs[-1]['commit']['committed_date'][0:-6])
#                     # res = {
#                     #     'name': project['name'],
#                     #     'date': date
#                     # }
#                     projects.append({
#                         'name': project['name'],
#                         'date': date,
#                         'start': b['commit']['committed_date'][0:-6],
#                         'end': branchs[-1]['commit']['committed_date'][0:-6]
#                     })
#                     break
#             else:
#                 projects.append({
#                     'name': 'name',
#                     'date': 'no master'
#                     ''
#                 })

projects.sort(key=lambda x:x['date'],reverse=True)

print json.dumps(projects,indent=4)
print len(projects)
print datetime.datetime.now()-starttime
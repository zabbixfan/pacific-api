#coding: utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')
from app import db
from ..models.repo import Repo,History
from ..common.time_helper import datetime_to_timestamp,datetime_to_strtime,strtime_to_datetime,current_datetime
from ..common.page_helper import PageResult
from ..common.string_helper import reg_parser
from config import Config
from ..common.searchrequest import searchRequest
import urllib,json
from flask import request
from app.tasks.backupdns import backup

def getRepoList(keyword=None,offset=0,limit=20):
    query = db.session.query(Repo)
    if keyword:
        keyword = keyword.replace('%', '')
        keyword = keyword.replace('_', '')
        keyword = keyword.replace('*', '')
        keyword = '%' + keyword + '%'
        query=query.filter(db.or_(Repo.repoId.like(keyword),Repo.url.like(keyword),Repo.name.like(keyword)))

    return PageResult(query.order_by(Repo.lastActivityAt.desc()),limit,offset).to_dict(lambda repo:{
        'repoId': repo.repoId,
        'name': repo.name,
        'url': repo.url,
        'createAt': datetime_to_strtime(repo.createAt),
        'lastActivityAt': datetime_to_strtime(repo.lastActivityAt),
        'lastPushMaster': datetime_to_strtime(repo.lastPushMaster) if repo.lastPushMaster else '',
        'path': repo.path,
        'isSync': "true" if repo.isSync == 1 else "false"
    })

def addToSearch(id=None):
    if id is None:
        return None
    query = db.session.query(Repo).filter(Repo.repoId == id).first()
    publickey = Config.SC_PUBK
    privatekey = Config.SC_PRIVATEK
    repousername = Config.GIT_USER
    repopassword = Config.GIT_PASS
    reponame = query.path.replace('/','-')
    reposource = query.url.replace('.git','')
    repourl = query.url
    repotype = "git"
    repobranch = "master"
    message = "pub=%s&reponame=%s&repourl=%s&repotype=%s&repousername=%s&repopassword=%s&reposource=%s&repobranch=%s" % (
            urllib.quote_plus(publickey),
            urllib.quote_plus(reponame),
            urllib.quote_plus(repourl),
            urllib.quote_plus(repotype),
            urllib.quote_plus(repousername),
            urllib.quote_plus(repopassword),
            urllib.quote_plus(reposource),
            urllib.quote_plus(repobranch)
        )
    url = '{}/api/repo/add'.format(Config.SC_URL)
    res = searchRequest(url,message,privatekey)
    if res['sucessful']:
        query.isSync = 1
        query.commit()
    return res

def delFromSearch(id=None):
    if id is None:
        return None
    query = db.session.query(Repo).filter(Repo.repoId == id).first()
    publickey = Config.SC_PUBK
    privatekey = Config.SC_PRIVATEK
    reponame = query.path.replace('/','-')
    message = "pub=%s&reponame=%s" % (
        urllib.quote_plus(publickey),
        urllib.quote_plus(reponame),
    )
    url = '{}/api/repo/delete'.format(Config.SC_URL)
    res = searchRequest(url,message,privatekey)
    if res['sucessful']:
        query.isSync = 0
        query.commit()
    return res



def getRepo(id=None):
    query = db.session.query(Repo).filter(Repo.repoId == id).first()
    return {
        'url':query.url,
        'name':query.name
    }
def paserUrl(url):
    res = reg_parser(str(url),'searchurl')
    if res:
        return urllib.unquote_plus(res.group(1))
    else:
        return urllib.unquote_plus(str(url))
def getHistory(keyword=None,offset=0,limit=20):
    query = db.session.query(History)
    if keyword:
        keyword = keyword.replace('%', '')
        keyword = keyword.replace('_', '')
        keyword = keyword.replace('*', '')
        keyword = '%' + keyword + '%'
        query=query.filter(db.or_(History.url.like(keyword),History.user.like(keyword)))

    return PageResult(query.order_by(History.id.desc()),limit,offset).to_dict(lambda history:{
        'id': history.id,
        'name': history.user,
        'url': paserUrl(history.url),
        #'url': history.url,
        'time': datetime_to_strtime(strtime_to_datetime(history.time,format_str='%d/%b/%Y:%H:%M:%S +0800'))
    })

def hook():
    res = json.loads(request.data)
    print json.dumps(res,indent=2)
    if 'event_name' in res.keys():
        if res['event_name'] == 'project_create':
            repo = Repo()
            repo.name = res['name']
            repo.owner = res['owner_name']
            repo.createAt = strtime_to_datetime(str(res['created_at']).replace('+08:00', ''),
                                                format_str="%Y-%m-%dT%H:%M:%S")
            repo.lastActivityAt = repo.createAt
            repo.path = res['path_with_namespace']
            repo.isSync = 0
            repo.url = '{}/{}.git'.format(Config.GITLAB_URL,res['path_with_namespace'])
            repo.save(wait_commit=True)
            repo.commit()
        if res['event_name'] == 'project_destroy':
            print 'enter project_destroy'
            Repo.query.filter(Repo.name == res['name']).delete()
            db.session.commit()
        if res['event_name'] == 'push' and res['ref'].endswith('master'):
            repo = Repo.query.filter(Repo.url == res['project']['git_http_url']).first()
            repo.lastPushMaster = current_datetime()
            repo.commit()


    return "..."

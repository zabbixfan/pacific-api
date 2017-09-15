import sys
#sys.path.append('../commio')
from ..common.searchrequest import searchRequest
from config import Config
from app import db,celery
from ..models.repo import Repo
import urllib,json

@celery.task()
def syncSearchCodeStatus():
    repos = db.session.query(Repo).all()
    publickey = Config.SC_PUBK
    privatekey = Config.SC_PRIVATEK
    message = "pub=%s" % (urllib.quote_plus(publickey))
    url = '{}/api/repo/list'.format(Config.SC_URL)
    res = searchRequest(url,message,privatekey)
    scUrls = [i['url'] for i in res['repoResultList']]
    syncRepo = {}
    for repo in repos:
        if repo.url not in scUrls:
            repo.isSync = 0

        else:
            repo.isSync = 1
        repo.commit()
        syncRepo[repo.url] = 'success'
    return syncRepo

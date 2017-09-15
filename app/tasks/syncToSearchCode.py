#coding: utf-8
from ..common.searchrequest import searchRequest
from config import Config
import requests
from app import db
from ..models.repo import Repo
from ..domain.repo import addToSearch
def searchSync():
    query = db.session.query(Repo).filter(Repo.isSync != 1).all()
    for repo in query:
        #print repo.url
        print addToSearch(repo.repoId)
        # data = {'repoUrl':repo.url}
        # url = '{}/api/repo/index/'.format(Config.SC_URL)
        # print url
        # r = requests.get(url=url,params=data)
        # res =  r.content
        # print res
        # if res['sucessful']:
        #     query.isSync = 1
        #     query.commit()
        # break
    # return res



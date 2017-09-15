#coding: utf-8
import requests
from ..models.repo import Repo
from ..common.time_helper import strtime_to_datetime
from config import Config
token=Config.GIT_PRIVATE_TOKEN
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
        # for res in r.json():
        #     rel.append(res)

    #rel = sorted(rel, key=lambda rel: rel['last_activity_at'], reverse=True)
    for i in rel:
        repo = Repo.query.filter(Repo.url == i['http_url_to_repo']).first()
        if repo is None:
            repo=Repo()
        if 'owner' in i.keys():
            repo.owner = i['owner']['name']
        repo.name = i['name']
        repo.path = i['path_with_namespace']
        repo.url = i['http_url_to_repo']
        repo.createAt = strtime_to_datetime(str(i['created_at']).replace('+08:00',''), format_str="%Y-%m-%dT%H:%M:%S.%f")
        repo.lastActivityAt = strtime_to_datetime(str(i['last_activity_at']).replace('+08:00',''), format_str="%Y-%m-%dT%H:%M:%S.%f")
        repo.save(wait_commit=True)
    repo.commit()
    print len(rel)

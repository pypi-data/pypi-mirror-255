import requests # token : gitlab_token
import os
import sys


def clone_projects(grp_id):
    url_projets= git_url+"groups/"+str(grp_id)+"/projects"
    projets  = requests.get(url_projets, headers=headers).json()
    for project in projets :
        path = root_path+project['path_with_namespace']
        if not os.path.isdir(path):
            os.makedirs(path)
            cmd = "git clone "+project['ssh_url_to_repo'] +" "+path
            stream = os.popen(cmd)
    url_grps = git_url+"groups/"+str(grp_id)+"/subgroups"
    subgroups = requests.get(url_grps, headers=headers).json()
    for subgroup in subgroups :
        clone_projects(subgroup['id'])

#"https://gitlab.com/"
#gitlab_token = os.environ['gitlab_token']
#root_path = "/tmp/"
#grp_id=10859288

grp_id = sys.argv[1]
root_path = sys.argv[2]

gitlab_token = os.environ['gitlab_token']
git_url = "https://gitlab.allence.cloud/"+"api/v4/"
if len(sys.argv) > 3:
    git_url = sys.argv[3]+"api/v4/"

headers = {'PRIVATE-TOKEN': gitlab_token}
clone_projects(str(grp_id))

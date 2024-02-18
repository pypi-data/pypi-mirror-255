import os
import requests
import gitlab
import sys
auto_mr_dev=False
auto_mr_uat=False
auto_mr_prod=False


if "true"==str(os.environ.get("AUTO_APPLY_DEV")).lower():
    auto_mr_dev=True
if "true"==str(os.environ.get("AUTO_APPLY_UAT")).lower():
    auto_mr_uat=True
if "true"== str(os.environ.get("AUTO_APPLY_PROD")).lower():
    auto_mr_prod=True

git_url="https://gitlab.allence.cloud"
if len(sys.argv) > 1:
    git_url = sys.argv[1]

merge_id = os.environ.get('CI_MERGE_REQUEST_IID')
project_id=os.environ.get('CI_PROJECT_ID')
gitlab_token=os.environ.get('gitlab_token')
gl = gitlab.Gitlab(git_url,private_token = gitlab_token)
project = gl.projects.get(project_id)
mr= project.mergerequests.get(merge_id)
changeList=[]
mrchange=mr.changes()
changes = mrchange['changes']
if (len(changes)==0):
    print("no changes detected in this mr")
    changeList.append("no changes detected in this mr")
else:
    for change in changes:
        newPath=change['new_path']
        if("live/1-dev") in newPath and auto_mr_dev==False:
            print("auto mr is disabled in dev, found changes in:" +newPath)
            changeList.append("auto mr is disabled in dev, found changes in:" +newPath)

        if("live/2-uat") in newPath and auto_mr_uat==False:
            print("auto mr is disabled in uat, found changes in:" +newPath)
            changeList.append("auto mr is disabled in uat, found changes in:" +newPath)
        if("live/3-prod") in newPath and auto_mr_prod==False:
            print("auto mr is disabled in prod, found changes in:" +newPath)
            changeList.append("auto mr is disabled in prod, found changes in:" +newPath)

if not changeList:
    base_url = "https://gitlab.allence.cloud/api/v4/projects/"+str(project_id)+"/merge_requests/"+str(merge_id)+"/merge?private_token="+gitlab_token#/merge"
    #print(base_url)
    merge =  requests.put(base_url)
    print(str(merge))
    if 'Branch cannot be merged' in str(merge) :
        base_url = "https://gitlab.allence.cloud/api/v4/projects/"+str(project_id)+"/merge_requests/"+str(merge_id)+"/rebase?private_token="+gitlab_token#/merge"
        rebase =  requests.put(base_url)
        print(str(rebase))

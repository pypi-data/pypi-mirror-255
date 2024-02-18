import requests
import os
import time

gitlab_token = os.environ.get("GITLAB_TOKEN")
projet_infra=os.getenv("PROJET_INFRA")
project_name = os.getenv("PROJECT_GROUP").replace('/','%2F')+"%2F"+projet_infra
branch_name = os.getenv("TERRAGRUNT_GIT_BRANCH")
headers = {'PRIVATE-TOKEN': gitlab_token}
base_url = "https://gitlab.allence.cloud/api/v4/projects/"
## GET INFRA PROJECT ID
project_url = base_url+project_name
req_project = requests.get(project_url, headers=headers).json()
project_id = req_project['id']
## GET INFRA MR ID
branch_url=base_url+str(project_id)+"/repository/branches/"+branch_name
req_branch=requests.get(branch_url, headers=headers).json()
commit_sha = req_branch['commit']['id']
print("commit ID = "+str(commit_sha))

mr_url=base_url+str(project_id)+"/repository/commits/"+commit_sha+"/merge_requests"
req_mr=requests.get(mr_url, headers=headers).json()
#print(req_mr)
mr_id = req_mr[0]['iid']
mr_title= req_mr[0]['title']
print("MR ID = "+str(mr_id))


mrs_url = base_url+str(project_id)+"/merge_requests?state=opened"
req_mrs =requests.get(mrs_url, headers=headers).json()
#print(req_mrs)
if('error' in req_mrs):
    print("Everything is fine no open MRs for this env")
else :
    for mr in req_mrs :
        if mr['iid'] != mr_id and mr['title']==mr_title:
            print("DELETE "+base_url+str(project_id)+"/merge_requests/"+str(mr['iid']))
            r = requests.delete(base_url+str(project_id)+"/merge_requests/"+str(mr['iid']), headers=headers)
            print("MR "+str(mr['iid'])+" is Closed, status: "+str(r))

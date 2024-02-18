
import requests
import os
gitlab_token = os.environ['gitlab_token']
headers = {'PRIVATE-TOKEN': gitlab_token}
project_id = os.environ['CI_PROJECT_ID']
base_url = "https://gitlab.allence.cloud/api/v4/projects/"+str(project_id)


req_mrs =requests.get(base_url+"/merge_requests?state=opened", headers=headers).json()
for mr in req_mrs :
    r = requests.put(base_url+"/merge_requests/"+str(mr['iid'])+"/rebase", headers=headers)
    print("MR "+str(mr['iid'])+" is rebased status: "+str(r))
    lastcommit_res =requests.get(base_url+"/repository/commits/"+str(mr['sha'])+"", headers=headers).json()




import requests
import os
import time
 

gitlab_token = os.getenv("gitlab_token")
headers = {'PRIVATE-TOKEN': gitlab_token}
base_url = "https://gitlab.allence.cloud/api/v4/projects/"

projet_infra=os.getenv("PROJET_INFRA")
projet_group=os.getenv("PROJECT_GROUP")
project_name = projet_group.replace("/","%2F")+"%2F"+projet_infra
branch_name = os.getenv("TERRAGRUNT_GIT_BRANCH")

## GET INFRA PROJECT ID
project_url = base_url+project_name
req_project = requests.get(project_url, headers=headers).json()
project_id = req_project['id']
print("project ID = "+str(project_id))
## GET INFRA MR ID
branch_url=base_url+str(project_id)+"/repository/branches/"+branch_name.replace("/","%2F")
req_branch=requests.get(branch_url, headers=headers).json()
commit_sha = req_branch['commit']['id']
print("commit ID = " +
      str(commit_sha))

mr_url=base_url+str(project_id)+"/repository/commits/"+commit_sha+"/merge_requests"
req_mr=requests.get(mr_url, headers=headers).json()
#print(req_mr)
mr_id = req_mr[0]['iid']
print("MR ID = " + str(mr_id))

time.sleep(5)
mr_url = base_url+str(project_id)+"/merge_requests/"+str(mr_id)
status = "running"
mr_validation = True
while status == "running" :
    mr_validation = True
    print("############################################")
    req_mr =requests.get(mr_url, headers=headers).json()
    status = req_mr['head_pipeline']['detailed_status']['label']
    print("The MR is " + status)
    jobs_url= base_url+str(project_id)+"/pipelines/"+str(req_mr['head_pipeline']['id'])+"/jobs"
    req_jobs = requests.get(jobs_url, headers=headers).json()
    for job in req_jobs:
        print("The Job "+job['name'] +" is "+job['status'])
        mr_validation = mr_validation and job['status'] == 'success'
    time.sleep(2)
if mr_validation:
    r = requests.put(mr_url+"/merge", headers=headers)
    print("MR "+str(req_mr['iid'])+" is Merged, status: "+str(r))
    print("Wait for the new Pipeline to be created")
    time.sleep(5)
    status = "running"
    mr_validation = True
    while status == "running" :
        print("############################################")
        commit_url= base_url+str(project_id)+"/repository/commits/"+str(req_mr['sha'])
        req_commit = requests.get(commit_url, headers=headers).json()
        mr_validation = True
        status = req_commit['last_pipeline']['status']
        jobs_url= base_url+str(project_id)+"/pipelines/"+str(req_commit['last_pipeline']['id'])+"/jobs"
        req_jobs = requests.get(jobs_url, headers=headers).json()
        for job in req_jobs:
            print("The Job "+job['name'] +" is "+job['status'])
        time.sleep(2)

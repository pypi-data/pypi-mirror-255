import requests



class GitlabFunctions:
    def __init__(self, gitlab_token,git_url):
        self.headers = {'PRIVATE-TOKEN': gitlab_token, 'Content-Type': 'application/json'}
        self.git_url = git_url

    def create_user(self, branch, path,  AwsUsername, keybase, project_id, action):

        postData = {
            'branch': branch,
            'commit_message': path,
            'actions': [
                {
                    'action': action,
                    'file_path': path + '/main.tf',
                    'content':
                        'provider "aws" {\n' +
                        '  region     = var.aws_region\n' +
                        '}\n' +
                        'module "user" {\n' +
                        '  source = "git::https://git@gitlab.com/commons-acp/terraform/aws/user.git?ref=v1.0.0"\n' +
                        '  name                              = "' + AwsUsername + '"\n' +
                        '  groups                            = [var.grp_devops_name]\n' +
                        '  force_destroy                     = true\n' +
                        '  pgp_key                           = "keybase:' + keybase + '"\n' +
                        '}'
                },
                {
                    'action': action,
                    'file_path': path + '/Makefile',
                    'content':
                        'credentials:\n' +
                        '\t@echo "####User name #####"\n' +
                        '\t@terraform output "user_name"\n' +
                        '\t@echo "#####PASSWORD####"\n' +
                        '\t@terraform output "encrypted_password" | base64 --decode | keybase pgp decrypt\n' +
                        '\t@echo ""\n' +
                        '\t@echo "#####TOKEN KEY####"\n' +
                        '\t@terraform output "access_key_id"\n' +
                        '\t@echo "####TOKEN SECRET#####"\n' +
                        '\t@terraform output "encrypted_secret_access_key" | base64 --decode | keybase pgp decrypt\n' +
                        '\t@echo ""\n' +
                        '\t@echo "Gardes ces acces secret utilise uniquement terraform pour les operations"\n'
                },
                {
                    'action': action,
                    'file_path': path + '/outputs.tf',
                    'content':
                        'output "user_name" {\n' +
                        '  value = module.user.aws_iam_user-credentials.name\n' +
                        '}\n' +
                        'output "access_key_id" {\n' +
                        '  value = module.user.aws_iam_user-credentials.access-key-id\n' +
                        '}\n' +
                        '#terraform output encrypted_password | base64 --decode | keybase pgp decrypt\n' +
                        'output "encrypted_secret_access_key" {\n' +
                        '  value = module.user.aws_iam_user-credentials.encrypted-secret-access-key\n' +
                        '}\n' +
                        '# terraform output encrypted_password | base64 --decode | keybase pgp decrypt\n' +
                        'output "encrypted_password" {\n' +
                        '  value = module.user.aws_iam_user-credentials.encrypted_password\n' +
                        '}'
                },
                {
                    'action': action,
                    'file_path': path + '/terragrunt.hcl',
                    'content':
                        'include {\n' +
                        '  path = find_in_parent_folders()\n' +
                        '}\n' +
                        '\n' +
                        '\n' +
                        '\n' +
                        'dependency "groups"{\n' +
                        '  config_path = "../../groups"\n' +
                        '}\n' +
                        'inputs = {\n' +
                        '  grp_devops_name = dependency.groups.outputs.grp_devops_name\n' +
                        '  aws_region = "eu-west-1"\n' +
                        '}'
                },
                {
                    'action': action,
                    'file_path': path + '/variables.tf',
                    'content':
                        'variable "aws_region" {\n' +
                        '  description = "AWS region"\n' +
                        '}\n' +
                        'variable "grp_devops_name" {\n' +
                        '  description = "Group devops name"\n' +
                        '}\n'
                }

            ]
        }

        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/repository/commits"
        add = requests.post(url, json=postData, headers=self.headers)


    def create_branch(self,  project_id, branch_name):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/repository/branches?branch=' + branch_name+'&ref=master'
        return requests.post(url, "", headers=self.headers)

    def get_all_project_branches(self, project_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/repository/branches?per_page=100"
        return requests.get(url, headers=self.headers).json()

    def delete_branch(self, project_id, branchName):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/repository/branches/"+str(branchName)
        return requests.delete(url, headers=self.headers)

    def get_single_commit(self,  project_id, commit_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/repository/commits/' + str(commit_id)
        return requests.get(url,  headers=self.headers).json()

    def get_last_mr_commit_id(self,  project_id, mr_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/' + str(mr_id) + '/commits'
        return requests.get(url, headers=self.headers).json()

    def get_full_commit_by_id(self,  project_id, commit_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/repository/commits/' + str(commit_id)
        return requests.get(url,  headers=self.headers)

    def get_pipeline_jobs(self,  project_id, last_pipeline_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/pipelines/' + str(last_pipeline_id)+'/jobs'
        return requests.get(url,  headers=self.headers).json()

    def merge_request(self,  project_id, branch_name, main_branch):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/?id='+str(project_id)+'&title=auto_mr_'+branch_name+'&source_branch='+branch_name+'&target_branch='+main_branch
        return requests.post(url, "", headers=self.headers)

    def accept_merge_request(self, project_id, mr_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/' + str(mr_id)+'/merge?should_remove_source_branch=true'
        return requests.put(url, "", headers=self.headers)

    def delete_merge_request(self, project_id, mr_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/merge_requests/" + str(mr_id)
        return requests.delete(url, headers=self.headers)

    def get_all_project_merge_requests(self, project_id,  created_before):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/?state=opened&created_before='+str(created_before)+'&per_page=1'
        return requests.get(url,  headers=self.headers).json(),

    def get_all_merge_request_by_project_id(self, project_id, mr_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/' + str(mr_id)
        return requests.get(url,  headers=self.headers).json()

    def get_all_merge_request(self, project_id, created_before):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/?state=all&created_before='+str(created_before)+'&per_page=10'
        return requests.get(url,  headers=self.headers).json()

    def get_all_merge_request_by_page(self, project_id, created_before, limit):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/?state=opened&created_before='+str(created_before)+'&per_page=20&page=' + str(limit)
        return requests.get(url,  headers=self.headers).json()

    def get_number_merge_request_project(self, project_id, created_before, limit, page):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/?state=opened&created_before='+str(created_before)+'&per_page='+str(limit) +'&page=' + str(page)
        return requests.get(url,  headers=self.headers).json()

    def get_number_merge_request_group(self, group_id, created_before, limit, page):
        url = self.git_url + "/api/v4/groups/" + str(group_id) + '/merge_requests/?state=opened&created_before='+str(created_before)+'&per_page='+str(limit) +'&page=' + str(page)
        return requests.get(url,  headers=self.headers).json()

    def update_mr_state(self , project_id, iid):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/merge_requests/' + str(iid)
        return requests.put(url, data='{"state_event": "close"}', headers=self.headers).json()

    def get_all_group_merge_requests(self, group_id,  created_before):
        url = self.git_url + "/api/v4/groups/" + str(group_id) + '/merge_requests/?state=opened&created_before='+str(created_before)
        return requests.get(url,  headers=self.headers).json()

    def get_all_group_merge_requests_per_page(self, group_id,  created_before, limit):
        url = self.git_url + "/api/v4/groups/" + str(group_id) + '/merge_requests/?state=opened&created_before='+str(created_before)+'&per_page=20&page=' + str(limit)
        return requests.get(url,  headers=self.headers).json()

    def get_job_trace(self, project_id, job_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + '/jobs/' + str(job_id)+'/trace'
        return requests.get(url, headers=self.headers).text

    def get_services(self, project_id,  page):
        url = self.git_url + "/api/v4/projects/" + str(
            project_id) + "/repository/tree?recursive=true&per_page=20&page=" + str(page)
        return requests.get(url, headers=self.headers).json()

    def get_file_content(self, project_id, path_replaced):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/repository/files/" + path_replaced + '?ref=master'
        return requests.get(url, headers=self.headers).json()

    def get_project_by_id(self, project_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id)
        return requests.get(url, headers=self.headers).json()

    def get_group_by_id(self, group_id):
        url = self.git_url + "/api/v4/groups/" + str(group_id)
        return requests.get(url, headers=self.headers).json()

    def get_projects_of_group(self, group_id, page, per_page):
        url = self.git_url + "/api/v4/groups/" + str(group_id) + "/projects?per_page=" + str(per_page) + "&page=" + str(page)
        return requests.get(url, headers=self.headers).json()

    def current_group_project(self, project_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id)
        web_url_project = requests.get(url, headers=self.headers).json()['web_url']
        name_project = requests.get(url, headers=self.headers).json()['name']
        url_group = self.git_url + "/api/v4/projects/" + str(project_id) + "/groups"
        url_groups = requests.get(url_group, headers=self.headers).json()
        for group in url_groups:
            if str(group['web_url']).replace("/groups", "")+"/"+name_project == web_url_project:
                return group

    def check_project_infra_exist(self, group_id):
        url = self.git_url + "/api/v4/groups/" + str(group_id) + "/projects"
        projects = requests.get(url, headers=self.headers).json()
        for pr in projects:
            if pr['name'] == "infra":
                return pr['id']

    def get_project_pipeline(self, project_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/pipelines"
        return requests.get(url, headers=self.headers).json()

    def check_with_user_folder(self, project_id):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/repository/tree?path=live/aws/global/iam/users"
        return requests.get(url, headers=self.headers).json()

    def get_user_tfstate(self, project_id, gitlab_username):
        url = self.git_url + "/api/v4/projects/" + str(project_id) + "/terraform/state/aws_global_iam_users_" + str(gitlab_username)
        return requests.get(url, headers=self.headers).json()

    # def delete_file_of_repo(self):
    #     print()



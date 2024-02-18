from terragit.utilsFunctions import *
from terragit.terragrunt import *


class AddUserGitlabRepo:
    def __init__(self, gitlab_token, git_url):
        self.gitlab_token = gitlab_token
        self.git_url = git_url
        self.gitlab_functions = GitlabFunctions(gitlab_token, git_url)
        self.bcolor = bcolors()
        self.utils_functions = UtilsFunctions(gitlab_token, git_url)

    def add_user(self, project_id, grp_id, gitlab_username, access_level, exist, keybase):
        headers = {'PRIVATE-TOKEN': self.gitlab_token}
        if "user does not exist in gitlab group" in exist:
            if access_level.lower() == "guest":
                level = 10
            elif access_level.lower() == "reporter":
                level = 20
            elif access_level.lower() == "developer":
                level = 30
            elif access_level.lower() == "maintainer":
                level = 40
            elif access_level.lower() == "owner":
                level = 50
            url = self.git_url + "/api/v4/users?username=" + str(gitlab_username)
            user = requests.get(url, headers=headers).json()
            if grp_id is not None:
                url = self.git_url + "/api/v4/groups/" + str(grp_id) + "/members?user_id=" + str(
                    user[0]['id']) + "&access_level=" + str(level)
                add = requests.post(url, headers=headers)
        if "IAM user not found" in exist:
            self.utils_functions.apply_service(project_id, self.gitlab_token, "addUser", "create_user", "master",
                                               gitlab_username, keybase)

    def check_user_existance(self, project_id, grp_id, gitlab_username):
        headers = {'PRIVATE-TOKEN': self.gitlab_token}
        exist = ""
        url = self.git_url + "/api/v4/users?username=" + str(gitlab_username)
        user = requests.get(url, headers=headers).json()
        try:
            url = self.git_url + "/api/v4/groups/" + str(grp_id) + "/members/all?user_ids=" + str(user[0]['id'])
            exist = requests.get(url, headers=headers).json()
            # print("exist", exist)
            if len(exist) > 0:
                exist = "user exist in gitlab group & "
            else:
                exist = "user does not exist in gitlab group & "
        except:
            exist = "problem occured while checking user existance in gitlab "
            print(bcolors.FAIL, exist)
            return exist
        res = self.utils_functions.check_content_existance_in_service(project_id,
                                                                      'https://git@gitlab.com/commons-acp/terraform/aws/user.git',
                                                                      'name="' + gitlab_username + '"')
        if "content_found" in res:
            print(bcolors.OKGREEN, exist + "IAM user found")
            return exist + "IAM user found"
        else:
            print(bcolors.OKGREEN, exist + "IAM user found")
            return exist + "IAM user not found"

    def existance_gitlab(self, project_id, group_id, gitlab_username):

        headers = {'PRIVATE-TOKEN': self.gitlab_token}
        url = self.git_url + "/api/v4/users?username=" + str(gitlab_username)
        user = requests.get(url, headers=headers).json()

        if len(user) != 0:

            if project_id is not None:
                url = self.git_url + "/api/v4/projects/" + str(project_id) + "/members/all/" + str(user[0]['id'])
                exist = requests.get(url, headers=headers).json()
                try:
                    if 'message' in exist:
                        exist = "user does not exist in gitlab project & "
                    else:
                        exist = "user exist in gitlab project & "
                    return exist, user[0]['id']
                except:
                    exist = "problem occured while checking user existance in gitlab "
                    print(bcolors.FAIL, exist)
                    return exist, user[0]['id']
            if group_id is not None:

                url = self.git_url + "/api/v4/groups/" + str(group_id) + "/members/all/" + str(user[0]['id'])

                exist = requests.get(url, headers=headers).json()

                try:
                    if 'message' in exist:
                        exist = "user does not exist in gitlab project & "
                    else:
                        exist = "user exist in gitlab project & "
                    return exist, user[0]['id']
                except:
                    exist = "problem occured while checking user existance in gitlab "
                    print(bcolors.FAIL, exist)
                    return exist, user[0]['id']
        else:
            print(self.bcolor.WARNING, " no user found in gitlab using this username")

    def add_user_repository(self, project_id, group_id, gitlab_username, access_level, exist):

        exist_infra = int
        if exist is not None:
            if "user does not exist in gitlab project & " in exist[0]:
                if project_id is not None:
                    current_group = self.gitlab_functions.current_group_project(project_id)
                    exist_infra = self.gitlab_functions.check_project_infra_exist(current_group['id'])
                if group_id is not None:
                    exist_infra = self.gitlab_functions.check_project_infra_exist(group_id)

                if exist_infra is None:
                    print(bcolors.FAIL + " there is no infra project in this group")
                else:
                    self.gitlab_functions.create_branch(exist_infra, gitlab_username + "-patch" + str(exist_infra))
                    if project_id is not None:
                        Data = {
                            'branch': gitlab_username + "-patch" + str(exist_infra),
                            'commit_message': 'adding membership for a user ' + gitlab_username + ' to project',
                            'actions': [
                                {
                                    'action': 'create',
                                    'file_path': 'live/git/users/'+gitlab_username+'/main.tf',
                                    'content':
                                        'terraform  {\n' +
                                        '  required_providers {\n' +
                                        '    gitlab = {\n' +
                                        '       source  = "gitlabhq/gitlab"\n' +
                                        '       version = ">= 3.20.0"\n' +
                                        '     }\n' +
                                        '  }\n' +
                                        '}\n'
                                        '\n'
                                        'resource "gitlab_project_membership" "membership" {\n' +
                                        '  project_id = "' + str(project_id) + '"\n' +
                                        '  user_id = "' + str(exist[1]) + '"\n' +
                                        '  access_level = "' + access_level.lower() + '"\n' +
                                        '}\n'

                                },
                                {
                                    'action': 'create',
                                    'file_path': 'live/git/users/'+gitlab_username+'/terragrunt.hcl',
                                    'content':
                                        'include {\n' +
                                        '  path = find_in_parent_folders()\n' +
                                        '}\n'
                                },

                            ]
                        }
                    if group_id is not None:
                        Data = {
                            'branch': gitlab_username + "-patch" + str(exist_infra),
                            'commit_message': 'adding membership for a user ' + gitlab_username + ' to group',
                            'actions': [
                                {
                                    'action': 'create',
                                    'file_path': 'live/git/users/'+gitlab_username+'/main.tf',
                                    'content':
                                        'terraform  {\n' +
                                        '  required_providers {\n' +
                                        '    gitlab = {\n' +
                                        '       source  = "gitlabhq/gitlab"\n' +
                                        '       version = "= 3.20.0"\n' +
                                        '     }\n' +
                                        '  }\n' +
                                        '}\n'
                                        '\n'
                                        'variable "gitlab_token" {}\n'
                                        '\n'
                                        'resource "gitlab_group_membership" "membership" {\n' +
                                        '  group_id = "' + str(group_id) + '"\n' +
                                        '  user_id = "' + str(exist[1]) + '"\n' +
                                        '  access_level = "' + access_level.lower() + '"\n' +
                                        '}\n'
                                        'provider "gitlab" {\n'
                                        'token = var.gitlab_token\n'
                                        'base_url = "https://gitlab.allence.cloud/api/v4/"\n'
                                        '}\n'

                                },
                                {
                                    'action': 'create',
                                    'file_path': 'live/git/users/'+gitlab_username+'/terragrunt.hcl',
                                    'content':
                                        'include {\n' +
                                        '  path = find_in_parent_folders()\n' +
                                        '}\n'
                                        'inputs = {\n'
                                        'gitlab_token = get_env("gitlab_token")\n'
                                        '}\n'
                                },



                            ]
                        }
                    url = self.git_url + "/api/v4/projects/" + str(exist_infra) + "/repository/commits"
                    add = requests.post(url, json=Data, headers={'PRIVATE-TOKEN': self.gitlab_token})

                    mr_request_creation = self.gitlab_functions.merge_request(exist_infra, gitlab_username + "-patch" + str(exist_infra), "master")
                    while mr_request_creation.json()['pipeline'] is None:
                        mr = self.gitlab_functions.get_all_merge_request_by_project_id(exist_infra, mr_request_creation.json()['iid'])
                        if mr['pipeline'] is not None:
                            accept_mr = self.gitlab_functions.accept_merge_request(exist_infra, mr['iid'])
                            if mr['state'] == 'merged':
                                break




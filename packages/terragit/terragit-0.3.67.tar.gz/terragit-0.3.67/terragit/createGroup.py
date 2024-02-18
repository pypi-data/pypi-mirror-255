import shutil

import terragit.terragrunt as terraconf
import gitlab
import os , fileinput
import base64
from terragit.gitlabFunctions import *
import re
from string import Template
import requests


class Create:
    def __init__(self):
        self.bcolor = terraconf.bcolors
        self.gitlab_functions = GitlabFunctions('glpat-BS_yy1VSPx2PKkbjokN3', 'https://gitlab.allence.cloud')

    def create_group(self, group_name):

        fondation_id ='1539'
        git_url = 'https://gitlab.allence.cloud'
        gitlab_token = os.environ.get('gitlab_token')
        gl = gitlab.Gitlab(url=git_url, private_token=gitlab_token)
        foundation = gl.projects.get(fondation_id)
        f1 = foundation.files.get(file_path='live/prod/clients-acp/chosa/git/main.tf', ref='master')
        f3 = foundation.files.get(file_path='live/prod/clients-acp/chosa/git/terragrunt.hcl', ref='master')
        file_content1 = base64.b64decode(f1.content).decode("utf-8")
        file_content3 = base64.b64decode(f3.content).decode("utf-8")
        path = "tf_files"
        isExist = os.path.exists(path)
        if not isExist:
            os.mkdir('terragit/tf_files')
        f1 = open("terragit/tf_files/main.tf", "w")
        f1.write(file_content1)
        f1.close()
        f2 = open("terragit/tf_files/terragrunt.hcl", "w")
        f2.write(file_content3)
        f2.close()
        f3 = open("terragit/tf_files/master.tfvars", "w")
        f3.write('')
        f3.close()

        file = open("terragit/tf_files/main.tf", "r")
        file1 = open("terragit/tf_files/main.tf", "r")
        replacement = ""
        replacement2 = ""
        old_module = 'source = "git::https://git@gitlab.com/commons-acp/terraform/gitlab/acp-instance.git?ref=v1.0.11"'
        new_module = 'source = "git@gitlab.allence.cloud:commons-acp/terraform/gitlab/acp-instance.git?ref=1.8.0"'

        for line in file:
            line = line.strip()
            changes = line.replace(old_module, new_module)
            replacement = replacement + changes + "\n"
        fout = open("terragit/tf_files/main.tf", "w")
        fout.write(replacement)
        fout.close()
        for line in file1:
            line = line.strip()
            changes2 = line.replace('project_name ="chosa"', 'project_name' + ' ="'+ group_name +'"')
            replacement2 = replacement2 + changes2 + "\n"
        file1.close()
        fout1 = open("terragit/tf_files/main.tf", "w")
        fout1.write(replacement2)
        fout1.close()

        old = "provider "+'"gitlab" '+"{"
        new = 'base_url = "https://gitlab.allence.cloud/api/v4/"'
        for line in fileinput.FileInput('terragit/tf_files/main.tf', inplace=True):
            if old in line :
                line += new + os.linesep
            print(line, end="")

        old = "root_id = dependency.parent.outputs.root_id"
        new = 'gitlab_token = get_env("gitlab_token")'

        for line in fileinput.FileInput('terragit/tf_files/terragrunt.hcl', inplace=True):
            if old in line :
                line += new + os.linesep
            print(line, end="")

        self.gitlab_functions.create_branch(fondation_id, group_name + "-patch" + str(fondation_id))

        path ='live/prod/clients-acp/'
        with open('terragit/tf_files/terragrunt.hcl', 'r') as file:
            data1 = file.read()

        with open('terragit/tf_files/main.tf', 'r') as file:
            data2 = file.read()

        with open('terragit/tf_files/master.tfvars', 'r') as file:
            data3 = file.read()

        data= {
            "branch": group_name + "-patch" + str(fondation_id),
            "commit_message": "add acp-instance to clients acp",
            "start_branch": group_name + "-patch" + str(fondation_id),
            "actions": [
                {
                    "action": "create",
                    "file_path": path+group_name+'/git/main.tf',
                    "content": data2
                },
                {
                    "action": "create",
                    "file_path": path+group_name+'/git/master.tfvars',
                    "content": data3
                },
                {
                    "action": "create",
                    "file_path": path+group_name+'/git/terragrunt.hcl',
                    "content": data1
                }
            ]
        }

        url = git_url + "/api/v4/projects/" + str(fondation_id) + "/repository/commits"
        add = requests.post(url, json=data, headers={'PRIVATE-TOKEN': gitlab_token})
        mr_request_creation = self.gitlab_functions.merge_request(fondation_id, group_name + "-patch" + str(fondation_id), "master")
        while mr_request_creation.json()['pipeline'] is None:
            mr = self.gitlab_functions.get_all_merge_request_by_project_id(fondation_id, mr_request_creation.json()['iid'])
            if mr['pipeline'] is not None:
                accept_mr = self.gitlab_functions.accept_merge_request(fondation_id, mr['iid'])
                if mr['state'] == 'merged':
                    shutil.rmtree(os.getcwd()+'/terragit/tf_files')
                    break



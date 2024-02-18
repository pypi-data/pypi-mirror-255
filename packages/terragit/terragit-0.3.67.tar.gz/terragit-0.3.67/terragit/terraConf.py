from os.path import exists
import json
import os
from terragit.utilsFunctions import *
import subprocess
import terragit.keybaseFunctions as keybaseFunctions
import terragit.clone as clone
import terragit.terragrunt as terragrunt
import terragit.utilsFunctions as utils
import terragit.gitlabFunctions as GitlabFunctions


class TerraConf:
    def __init__(self):
        self.bcolor = terragrunt.bcolors

    def init_file(self):
        conf = {}
        for value in ['gitlab_token', 'gitlab_username','gitlab_url','keybase' ]:
            if value == "keybase":
                keybase_api = keybaseFunctions.KeybaseFunctions()
                verif = "false"
                while verif == "false":
                    val = input("Enter your " + value + ": ")
                    check = keybase_api.check_keybase_username_existance(str(val))
                    if check['them'][0] is None:
                        print(self.bcolor.FAIL + "this keybase username does not exist please retry")
                    else:
                        verif = "true"
            else:
                val = input("Enter your " + value + ": ")
            conf[value] = val
        exist = exists(os.path.expanduser(os.path.join("~/.terragit")))

        if not exist:

            file = open(os.path.expanduser(os.path.join("~/.terragit")), mode='w')
            file.write(
                '{ "gitlab_token": "' + conf['gitlab_token'] + '",\n' +
                '"gitlab_user": "' + conf['gitlab_username'] + '",\n' +
                '"gitlab_url": "' + conf['gitlab_url'] + '",\n' +
                '"keybase": "' + conf['keybase'] + '",\n' +
                '"projects": [] }\n '
            )
        else:
            file = open(os.path.expanduser(os.path.join("~/.terragit")))
            content = json.loads(file.read())
            file.close()
            file = open(os.path.expanduser(os.path.join("~/.terragit")), mode='w')
            content['gitlab_token'] = conf['gitlab_token']
            content['gitlab_user'] = conf['gitlab_username']
            content['gitlab_url'] = conf['gitlab_url']
            content['keybase'] = conf['keybase']

            json.dump(content, file, indent=3)
        file.close()
        print(self.bcolor.OKGREEN, " Terragit has been successfully initiated")


    def get_file_content(self):
        file = open(os.path.expanduser(os.path.join("~/.terragit")))

        json_object = json.loads(file.read())

        file.close()
        return json_object

    def list_projects(self, json_object):
        print(self.bcolor.OKGREEN, "your projects", json_object["projects"])

    def verif_file_and_credentials_existence(self):

        if exists(os.path.expanduser(os.path.join("~/.terragit"))):

            file = open(os.path.expanduser(os.path.join("~/.terragit")))

            json_object = json.loads(file.read())

            file.close()

            if (len(json_object["gitlab_token"]) > 0) and (len(json_object["gitlab_user"]) > 0) and (
                    len(json_object["keybase"]) > 0) and (len(json_object["gitlab_url"]) > 0):
                return json_object
        return 'false'

    def get_selected_project(self, content):
        for grp_name in list(content.keys())[4:]:
            if content[grp_name]['selected'] == 'true':
                print(self.bcolor.OKGREEN, " your Current selected project is ", content[grp_name])
                return content[grp_name]
        print(self.bcolor.WARNING, " no project is selected")

    def clone_and_switch(self, content, group_id, group_name, pwd):

        #

        colors = terragrunt.bcolors()

        gitlab_url = "https://gitlab.allence.cloud"

        verif = self.verif_file_and_credentials_existence()
        print(colors.OKCYAN, "Cloning ...")
        clonn = clone.Clone(verif["gitlab_token"], gitlab_url, pwd)
        clonn.clone_projects(None, group_id)
        print(colors.OKCYAN, "Checking the existance of IAM user ...")
        utilsFunctions = utils.UtilsFunctions(verif["gitlab_token"], gitlab_url)
        gt = GitlabFunctions.GitlabFunctions(verif["gitlab_token"], gitlab_url)
        service_path = utilsFunctions.check_content_existance_in_serviceGr(group_id, None,
                                                                           'https://git@gitlab.allence.cloud/commons-acp/terraform/aws/user.git',
                                                                           'name="' + verif["gitlab_user"] + '"')

        if "content_found" in service_path:
            print(colors.OKGREEN, "IAM user found!")

            self.add_credentials_to_group(gitlab_url, verif["gitlab_token"], group_id,
                                          None, pwd, "/" + service_path[29:service_path.rindex("/")], "true")
        else:
            print("IAM user not found")
            self.add_credentials_to_group(gitlab_url, verif["gitlab_token"], group_id,
                                          None, pwd, "", "false")

        self.switch_project_existant(content, group_id, group_name)
    def current_path(self):
        pwd = os.popen('pwd').read().rstrip()
        pwd = pwd + "/"
        return pwd
    def goTo_or_create_folder(self, path):
        print("hello from fc go to")
        cmd = "mkdir "+path
        if(subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)):
            print("creating f")
            return path
        else:
            print(" f exists")
            return path

    def switch_project(self, content, group_id, group_name):
        if self.check_project_existance(content, group_id, group_name):
            print("project is already cloned!!")
            self.switch_project_existant(content, group_id, group_name)
        else:
            print("we are going to clone the project for you")
            pwd = os.popen('pwd').read().rstrip()
            pwd = pwd + "/"

            self.clone_and_switch(content, group_id, group_name, pwd)

    def check_project_existance(self, content, group_id, group_name):
        exist = False
        for grp_name in list(content.keys())[4:]:
            if group_name == grp_name:
                if content[group_name]['group_id'] == group_id:
                    exist = True
                    return exist
        return exist

    def switch_project_existant(self, content1, group_id, group_name):
        print("switch_project_existant")
        switched = True
        content = self.get_file_content()

        for grp_name in list(content.keys())[4:]:
            if group_name == grp_name:
                if content[group_name]['group_id'] == group_id:
                    content[group_name]['selected'] = 'true'
                    if content[group_name]['aws_credentials']['secret_access_key'] != None:

                        cmd4 = "export GROUP_ID=" + group_id +"\n"
                        cmd3 = "export GITLAB_USER_NAME=" + content["gitlab_user"] + " \n" + " export gitlab_token=" + \
                           content["gitlab_token"]
                        cmd2 = "export AWS_SECRET_ACCESS_KEY=" + content[group_name]['aws_credentials']['secret_access_key']
                        cmd1 = " \n export AWS_ACCESS_KEY_ID=" + content[group_name]['aws_credentials'][
                            'access_key'] + " \n " + cmd2 + " \n " + cmd3 + " \n " + cmd4

                        f  = open(os.path.expanduser(os.path.join("~/.terragit_profile")), "w")
                        f.write(cmd1)
                        f.close()
                        cmd= "aws --version"
                        child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                                 encoding='utf8')
                        streamdata = child.communicate()[0]
                        print("streamdata",streamdata)
                        rc = child.returncode
                        print("rc",rc)
                        if(rc >= 0):
                            cred=" echo you have no aws access_key to add for this profile/group/project "
                            print("aws-cli in installed")
                            if len(content[group_name]['aws_credentials']['access_key']) > 1:

                                aws_cmd= "aws configure set aws_access_key_id  " \
                                         ""+content[group_name]['aws_credentials']['access_key'] + " --profile "+ group_name

                                cred= aws_cmd
                            if len(content[group_name]['aws_credentials']['secret_access_key']) > 1:
                                aws_cmd1= "aws configure set aws_secret_access_key " + content[group_name]['aws_credentials']['secret_access_key']+" --profile "+ group_name
                                cred= cred+" && " + aws_cmd1


                            subprocess.Popen(cred, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                             encoding='utf8')
                        else:
                            print("please install aws-cli first")
                    switched = 'true'
                    print("Please run source ~/.terragit_profile")

            elif content[grp_name]['selected'] == 'true':
                content[grp_name]['selected'] = 'false'
        if not switched:
            print(self.bcolor.WARNING, " Error retrieving project")
        else:
            with open(os.path.expanduser(os.path.join("~/.terragit")), 'w') as f:
                json.dump(content, f, indent=3)
            print(self.bcolor.OKGREEN, " Switch to project " + group_name + " succeded")

    def add_credentials_to_group(self, git_url, gitlab_token, group_id, project_id, path1, service_path, exist):
        gitlab_functions1 = GitlabFunctions.GitlabFunctions(gitlab_token, git_url)
        if project_id == None:
            prj = gitlab_functions1.get_projects_of_group(group_id, 1, 10)
            for i in prj:
                prj_path = i['web_url']
                group_name = gitlab_functions1.get_group_by_id(group_id)['name']
                access_key_id = ""
                decrypted_secret_access_key = ""
                path = path1
                project_path = path
                if exist == "true":
                    print(self.bcolor.OKCYAN, "Getting & Decrypting credentials ...")
                    path = path + prj_path[len(git_url) + 1:len(prj_path)] + service_path
                    cmd = "cd " + path + " && export gitlab_token=" + gitlab_token + " && terragrunt output"
                    popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                             encoding='utf8')
                    lines = popen.communicate(input='\n')[0].split("\n")
                    access_key_id = ""
                    encrypted_secret_access_key = ""
                    for line in lines:
                        if "access_key_id" in line:
                            access_key_id = line[line.index('"') + 1:line.rindex('"')]
                        if "encrypted_secret_access_key" in line:
                            encrypted_secret_access_key = line[line.index('"') + 1:line.rindex('"')]
                            decrypted_secret_access_key = 'echo ' + '"' + encrypted_secret_access_key + '" |base64 --decode | keybase pgp decrypt'
                            decrypted_secret_access_key = os.popen(decrypted_secret_access_key).read()
                else:
                    print(self.bcolor.WARNING, "You don't have an AWS account in this project...")
                print(self.bcolor.OKCYAN, "Adding project info to .terragit file ...")
                content = self.get_file_content()
                if {"name": group_name, "group_id": group_id} not in content['projects']:

                    content['projects'].append({"name": group_name, "group_id": group_id})

                    content[group_name] = {"selected": "false", "group_id": group_id, "path": project_path,
                                           "aws_credentials": {
                                               "access_key": access_key_id,
                                               "secret_access_key": decrypted_secret_access_key
                                           }}
                    with open(os.path.expanduser(os.path.join("~/.terragit")), 'w') as f:
                        json.dump(content, f, indent=3)
                elif {"name": group_name, "group_id": group_id} in content['projects'] and content[group_name] == {
                    "selected": "false", "group_id": group_id, "path": project_path, "aws_credentials": {
                        "access_key": "",
                        "secret_access_key": ""
                    }}:
                    content[group_name] = {"selected": "false", "group_id": group_id, "path": project_path,
                                           "aws_credentials": {
                                               "access_key": access_key_id,
                                               "secret_access_key": decrypted_secret_access_key
                                           }}
                    with open(os.path.expanduser(os.path.join("~/.terragit")), 'w') as f:
                        json.dump(content, f, indent=3)
                else:
                    print("content existant dans .terragit!!")
                print(self.bcolor.OKGREEN, "Project information has been successfully added to .terragit")

        else:
            TerraConf.add_credentials(self, git_url, gitlab_token, group_id, project_id, path1, service_path, exist)

    def add_credentials(self, git_url, gitlab_token, group_id, project_id, path, service_path, exist):
        gitlab_functions1 = GitlabFunctions.GitlabFunctions(gitlab_token, git_url)
        prj_path = gitlab_functions1.get_project_by_id(project_id)['web_url']
        group_name = gitlab_functions1.get_group_by_id(group_id)['name']
        access_key_id = ""
        decrypted_secret_access_key = ""
        project_path = path
        if exist == "true":
            print(self.bcolor.OKCYAN, "Getting & Decrypting credentials ...")
            path = path + prj_path[len(git_url) + 1:len(prj_path)] + service_path
            cmd = "cd " + path + " && export gitlab_token=" + gitlab_token + " && terragrunt output"
            popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                     encoding='utf8')
            lines = popen.communicate(input='\n')[0].split("\n")
            access_key_id = ""
            encrypted_secret_access_key = ""
            for line in lines:
                if "access_key_id" in line:
                    access_key_id = line[line.index('"') + 1:line.rindex('"')]
                if "encrypted_secret_access_key" in line:
                    encrypted_secret_access_key = line[line.index('"') + 1:line.rindex('"') - 1]
            decrypted_secret_access_key = "echo " + encrypted_secret_access_key + " | base64 --decode | keybase pgp decrypt"
            decrypted_secret_access_key = os.popen(decrypted_secret_access_key).read()
        else:
            print(self.bcolor.WARNING, "You don't have an AWS account in this project...")
        print(self.bcolor.OKCYAN, "Adding project info to .terragit file ...")
        content = self.get_file_content()
        if {"name": group_name, "group_id": group_id} not in content['projects']:
            content['projects'].append({"name": group_name, "group_id": group_id})
            content[group_name] = {"selected": "false", "group_id": group_id, "path": project_path, "aws_credentials": {
                "access_key": access_key_id,
                "secret_access_key": decrypted_secret_access_key
            }}
            with open(os.path.expanduser(os.path.join("~/.terragit")), 'w') as f:
                json.dump(content, f, indent=3)
        print(self.bcolor.OKGREEN, "Project information has been successfully added to .terragit")

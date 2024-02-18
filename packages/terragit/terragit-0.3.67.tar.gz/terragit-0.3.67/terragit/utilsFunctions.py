import datetime
import os
import re
import base64
import sys
import time

import terragit.terragrunt as terragrunt
from terragit.gitlabFunctions import *
from terragit.keybaseFunctions import *
import subprocess



class UtilsFunctions:
    def __init__(self, gitlab_token, git_url):
        self.gitlab_functions = GitlabFunctions(gitlab_token, git_url)
        self.git_url = git_url
        self.gitlab_token = gitlab_token
        self.bcolor = terragrunt.bcolors
        self.keybase_function = KeybaseFunctions()


    def track_pipeline(self, project_id, mr_id, i):
        print('waiting for service to be created')
        print(self.bcolor.OKGREEN, "waiting for service to be created ")
        res = self.gitlab_functions.get_last_mr_commit_id(project_id, mr_id)
        if i == 1:
            time.sleep(5)
        commit = self.gitlab_functions.get_single_commit(project_id, res[0]['id'])
        jobs = self.gitlab_functions.get_pipeline_jobs(project_id, commit['last_pipeline']['id'])
        for job in jobs:
            if job['status'] == 'failed':
                return "failed " + str(job['id'])
            elif job['name'] == 'apply-all':
                if job['status'] == 'success':
                    return str(job['id'])
            elif job['stage'] == 'merge' and job['status'] == 'success':
                self.gitlab_functions.accept_merge_request(project_id, mr_id)
                return 'false'
        return 'false'

    def apply_service(self, project_id, gitlab_token, service_name, param, main_branch="master",
                      aws_username="", keybase=""):

        date = datetime.datetime.now()
        date_replaced = re.sub(r' ', '-', str(date))
        date_replaced = re.sub(r'\.', '-', str(date_replaced))
        date_replaced = re.sub(r':', '-', str(date_replaced))
        # print(date_replaced)
        self.gitlab_functions.create_branch(project_id, service_name + "-" + date_replaced)
        if param == "create_user":
            aws_username_replaced = re.sub(r'\.', '%2E', aws_username)
            self.gitlab_functions.create_user(service_name + '-' + str(date_replaced),
                                              'live/aws/global/iam/users/' + str(aws_username_replaced),
                                              str(aws_username), str(keybase), str(project_id))
        res = self.gitlab_functions.merge_request(project_id, service_name + "-" + str(date_replaced), main_branch)
        res = res.json()
        mr_id = str(res['iid'])
        job_id = 'false'
        i = 1
        while 'false' in job_id:
            time.sleep(5)
            job_id = self.track_pipeline(project_id, mr_id, i)
            i = i + 1
        # print("job_id", job_id)
        trace = self.gitlab_functions.get_job_trace(project_id, job_id)
        # print("trace", trace)
        if ('false' not in job_id) and ('failed' not in job_id):

            start = trace.rindex('Outputs:')
            end = trace.index('Uploading artifacts')
            outputs = trace[start:end]
            print(outputs)
            return outputs
        elif 'false' not in job_id:
            if ("Error:" in trace) and ("COULDNT PROCESS" in trace):
                error = trace[trace.index('Outputs:'):trace.index("COULDNT PROCESS")]
                print("error ", error)
            else:
                print("error configuration is not valid")

            return "error"

    def check_content_existance_in_service(self, project_id, service_template, content):
        page = 1
        per_page = 20
        while per_page == 20:
            services = self.gitlab_functions.get_services(project_id, page)
            page = page + 1
            per_page = len(services)
            for service in services:
               try:
                   if "main.tf" in service['path']:
                       path_replaced = re.sub(r'/', '%2F', service['path'])
                       path_replaced = re.sub(r'\.', '%2E', path_replaced)
                       res = self.gitlab_functions.get_file_content(project_id, path_replaced)
                       service_content = str(base64.b64decode(res['content'])).replace(" ", "")
                       if (service_template in service_content) and (
                           content in service_content):
                           return "content_found & service_path:" + service['path']
               except:
                   return service['message']
        return "content not found"

    def check_content_existance_in_serviceGr(self, group_id, project_id, service_template, content):
        if project_id!=None :
            return self.check_content_existance_in_service(project_id, service_template, content)
        else:
            pr= self.gitlab_functions.get_projects_of_group(group_id,1,10)
            for i in range(len(pr)):
                print("project of group", pr[i]['id'])
                if pr[i]['name'] == "infra":
                    return self.check_content_existance_in_service(pr[i]['id'], service_template, content)
                else:
                    continue

    def help(self):
        colors = terragrunt.bcolors()
        print(colors.OKGREEN + "Terragit functions:")
        print(colors.OKBLUE + "1-terragit config \n2-terragit {changes, validate, plan, apply, output} \n" +
              "3-terragit docs \n4-terragit clone \n5-terragit adduser \n6-terragit list \n"
              "7-terragit currentProject \n8-terragit switch \n9-terragit clean \n"

              )
        print(colors.OKBLUE + "")
        print()

    def add_aws_account(self, group_id, gitlab_username):

        project_infra_id = self.gitlab_functions.check_project_infra_exist(group_id)
        headers = {'PRIVATE-TOKEN': self.gitlab_token}
        url = self.git_url + "/api/v4/users?username=" + str(gitlab_username)
        user = requests.get(url, headers=headers).json()
        action = ""

        if len(user) == 0:
            print(self.bcolor.FAIL + "this username does not exist please retry")

        else:
            tf_state ={}
            list = []
            folders = self.gitlab_functions.check_with_user_folder(project_infra_id)

            if len(folders) == 0:
                print(self.bcolor.FAIL + " the path doesn't match with the  preconfigured one" + self.bcolor.ENDC)

            else:
                for i in range(0, len(folders)):
                    list.append(folders[i]['name'])

            if "." in gitlab_username:
                tfstate_name = str(gitlab_username).replace(".", "-")
            else:
                tfstate_name = gitlab_username
            tf_state = self.gitlab_functions.get_user_tfstate(project_infra_id, tfstate_name)

            if gitlab_username in list and (len(tf_state['outputs']) != 0 or 'message' in tf_state):
                print(self.bcolor.OKGREEN, "IAM user found in this account")
                value = input(self.bcolor.OKBLUE + "would you like to have your encrypted credentials "
                                                           " ? yes/no  ")

                if value == "no":
                    return
                else:

                    print(self.bcolor.OKGREEN, "PASSWORD : ", self.bcolor.WARNING
                                    + str(tf_state['outputs']['encrypted_password']['value']))
                    print(self.bcolor.OKGREEN, "AWS_ACCESS_KEY_ID : ", self.bcolor.WARNING
                                    + str(tf_state['outputs']['access_key_id']['value']))
                    print(self.bcolor.OKGREEN, "AWS_SECRET_ACCESS_KEY : ", self.bcolor.WARNING
                                    + str(tf_state['outputs']['encrypted_secret_access_key']['value']))
                    print(self.bcolor.OKGREEN, "USER_NAME : ", self.bcolor.WARNING
                                    + str(tf_state['outputs']['user_name']['value']))
            else:
                print(self.bcolor.OKGREEN, "IAM user not found in this account")
                value = input(self.bcolor.OKBLUE + "would you like to create an account? "
                                                   " ? yes/no  ")
                if value == "no":
                    return
                else:
                    value = input(self.bcolor.OKBLUE + " please provide your keybase: "
                                                   "")
                    check_keybase = self.keybase_function.check_keybase_username_existance(value)
                    if check_keybase['them'] == [None]:
                        print(self.bcolor.FAIL, "Keybase not found , please check the provided name")
                    else:

                        self.gitlab_functions.create_branch(project_infra_id, gitlab_username + "-patch" + str(project_infra_id))
                        if len(tf_state['outputs']) == 0:
                            action = "delete"
                            self.gitlab_functions.create_user(str(gitlab_username) + "-patch" + str(project_infra_id),
                                                          'live/aws/global/iam/users/'+str(gitlab_username),
                                                           str(gitlab_username), str(value), str(project_infra_id), action)
                        action = "create"
                        self.gitlab_functions.create_user(str(gitlab_username) + "-patch" + str(project_infra_id),
                                                          'live/aws/global/iam/users/'+str(gitlab_username),
                                                           str(gitlab_username), str(value), str(project_infra_id), action)
                        mr_request_creation = self.gitlab_functions.merge_request(project_infra_id, gitlab_username + "-patch" + str(project_infra_id), "master")
                        job_id = 'false'
                        i = 1
                        while 'false' in job_id:
                            time.sleep(5)
                            job_id = self.track_pipeline(project_infra_id, mr_request_creation.json()['iid'], i)
                            i = i + 1
                        tfstate_created = self.gitlab_functions.get_user_tfstate(project_infra_id, tfstate_name)
                        print(self.bcolor.OKGREEN, "PASSWORD : ", self.bcolor.WARNING
                                + str(tfstate_created['outputs']['encrypted_password']['value']))
                        print(self.bcolor.OKGREEN, "AWS_ACCESS_KEY_ID : ", self.bcolor.WARNING
                                + str(tfstate_created['outputs']['access_key_id']['value']))
                        print(self.bcolor.OKGREEN, "AWS_SECRET_ACCESS_KEY : ", self.bcolor.WARNING
                                + str(tfstate_created['outputs']['encrypted_secret_access_key']['value']))
                        print(self.bcolor.OKGREEN, "USER_NAME : ", self.bcolor.WARNING
                                + str(tfstate_created['outputs']['user_name']['value']))

    def verify_before_hook(self):
        final_message = {}
        cmd = 'aws sts get-caller-identity --query "Arn" --output text | awk -F/ \'{print $NF}\''
        output = subprocess.check_output(cmd, shell=True)
        user = output.decode().strip()
        if user == "":
            print(self.bcolor.FAIL + "USER IN AWS DOES NOT EXIST! ")
            final_message['user'] = self.bcolor.FAIL + "USER IN AWS DOES NOT EXIST! "
        else:
            print(self.bcolor.OKGREEN + "USER IN AWS EXIST ! : \n" + user)
            final_message['user'] = str(self.bcolor.OKGREEN + "USER IN AWS EXIST ! : \n" + user)
        branch = ""
        if os.getenv("CI_JOB_TOKEN") is None:
            cmd1 = 'git branch --show-current'
            cmd2 = "git rev-parse --abbrev-ref HEAD"
            output1 = subprocess.check_output(cmd2, shell=True)
            branch = output1.decode().strip()
        else:
            branch = os.getenv("CI_COMMIT_BRANCH")
        final_message['branch'] = branch
        if branch != "master" and branch != "main":
            final_message['code'] = 1
        else:
            final_message['code'] = 0

        if final_message['code'] == 1:
            sys.exit(1)
        else:
            return final_message


# class setInterval:
#     def __init__(self, interval, action, project_id, mr_id,gitlab_token):
#         print('setInterval')
#         self.interval = interval
#         self.action = action
#         self.project_id = project_id
#         self.mr_id = mr_id
#         self.gitlab_token = gitlab_token
#         self.stopEvent = threading.Event()
#         thread = threading.Thread(target=self.__setInterval)
#         thread.start()
#
#     async def __setInterval(self):
#
#         print('__setInterval')
#         nextTime = time.time() + self.interval
#         while not self.stopEvent.wait(nextTime - time.time()):
#             print('while')
#             nextTime += self.interval
#             utils_functions = UtilsFunctions(self.gitlab_token, "https://gitlab.com")
#             job_id = utils_functions.track_pipeline(self.project_id, self.mr_id)
#             if 'false' not in job_id:
#                 return job_id
#
#     def cancel(self):
#         self.stopEvent.set()

import os
import terragit.terraConf as terraconf
import terragit.clone as clone


class TerraValidate:
    def __init__(self, gitlab_token, git_url):

        self.gitlab_token = gitlab_token
        self.git_url = git_url

    def validate_projects(self, local_path):
        # content = terraconf.TerraConf.get_file_content()
        print("hello from validate")
        # terraconf.TerraConf.check_project_existance(content, group_id, group_name)
        cmd = "touch validate.txt && cd " + local_path + " && terragrunt validate "
        print("cmd", cmd)
        os.system(cmd)
    def validate_distant(self, projectId, path):
        clone.Clone.clone_projects(self, projectId, None)
        cmd= "pwd"
        pwd = os.popen(cmd).read().rstrip()
        local_path = pwd+"/"+path
        print("local", local_path)
        self.validate_projects(local_path)
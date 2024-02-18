import requests  # token : gitlab_token
import os
import terragit.terragrunt as terraconf

class Clone:
    def __init__(self, gitlab_token, git_url, root_path):
        self.root_path = root_path
        self.gitlab_token = gitlab_token
        self.git_url = git_url
        self.bcolor = terraconf.bcolors

    def clone_projects(self, project_id, grp_id, path):

        if (path != None and path != "./"):
            headers = {'PRIVATE-TOKEN': self.gitlab_token}
            if path != None:
                root_path = os.path.abspath(path)

            if project_id != None:

                url_projets = self.git_url + "/api/v4/projects/" + str(project_id)
                project = requests.get(url_projets, headers=headers).json()
                path = root_path + "/" + project['path_with_namespace']
                if not os.path.isdir(path):
                    os.makedirs(path)

                    cmd = "cd "+ path +" && git clone " + project['ssh_url_to_repo']
                    os.system(cmd)

                else:
                    print(f"{path} already exists")

            if grp_id != None:

                url_projets = self.git_url + "/api/v4/groups/" + str(grp_id) + "/projects"

                projets = requests.get(url_projets, headers=headers).json()
                for project in projets:

                    path = root_path +'/'+ project['path_with_namespace']

                    if not os.path.isdir(path):
                        os.makedirs(path)
                        cmd = "cd "+ path +" && git clone " + project['ssh_url_to_repo']
                        os.system(cmd)
                    else:
                        print(f"{path} already exists")

                url_grps = self.git_url + "/api/v4/groups/" + str(grp_id) + "/subgroups"
                subgroups = requests.get(url_grps, headers=headers).json()
                for subgroup in subgroups:
                    self.clone_projects(None, subgroup['id'])
        else:
            print(self.bcolor.FAIL, " Can you provide a path for directory to make the clone when passing the args!!")

    def list_project(self, path):
        info_list = []
        group_id = 0
        user_input = ''
        headers = {'PRIVATE-TOKEN': self.gitlab_token}
        url_group = self.git_url + "/api/v4/groups/2875/descendant_groups"
        groups = requests.get(url_group, headers=headers).json()

        name_list = []

        for g in groups:
            data = {}
            data['name'] = g['name']
            data['id'] = g['id']

            info_list.append(data)
            name_list.append(g['name'])

        input_message = "Pick an option:\n"
        for index, item in enumerate(name_list):
            input_message += f'{index+1}) {item}\n'
        input_message += 'Make a choice to clone group: '
        while user_input.lower() not in name_list:
            user_input = input(input_message)
        print('You picked: ' + user_input)

        for j in info_list:
            if user_input == j['name']:
                group_id = j['id']

        if path != None:
            self.clone_projects(None, group_id, path)
        else:
            print(self.bcolor.FAIL, " Can you provide a path for directory to make the clone when passing the args!!")



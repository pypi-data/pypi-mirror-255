import json
import os
import re
import gitlab
import pandas as pd
from pandas import option_context

import terragit.terragrunt as terraconf


class Status:
    def __init__(self):
        self.bcolor = terraconf.bcolors

    def module(self):

        git_url = 'https://gitlab.allence.cloud'
        gitlab_token = os.environ.get('gitlab_token')

        mylist = []
        path_absolute = os.getcwd()
        for root, dirs, files in os.walk(path_absolute + "/live"):
            mylist.append(root)

        directories = []
        for r in mylist:
            if ".terraform" not in r and "build-front" not in r:
                file_exists = r + '/main.tf'
                isexist = os.path.exists(file_exists)
                if isexist:
                    directories.append(file_exists)
        modules = []
        tags = []

        for d in directories:
            with open(d) as temp_f:
                datafile = temp_f.readlines()
            for line in datafile:
                if 'module' in line:
                    for ligne in datafile:
                        if ligne.find('source') != -1 and ligne.find('git') != -1:
                            var = ligne.split("@", 1)[1]
                            new_address = re.sub(':', '/', var)
                            new_module = re.sub('"', "", new_address)
                            tags.append(new_module)

                            final = new_module.split('?', 1)[0]

                            if '.git' in final:
                                first_final = re.sub('.git', '', final)
                                last_final = first_final.split('/', 1)[1]
                                modules.append(last_final)
                            else:
                                last_final = final.split('/', 1)[1]
                                modules.append(last_final)
        last_tag = []
        gl = gitlab.Gitlab(url=git_url, private_token=gitlab_token)
        for m in modules:
            project_module = gl.projects.get(m)
            tag = project_module.tags.list()
            if len(tag) == 0:
                last_tag.append('no tag found')
            else:
                x = tag[0].attributes['name']
                last_tag.append(x)
        json_array = []
        for i in range(len(last_tag)):
            data = {}
            data['path'] = tags[i]
            data['recent_tag'] = last_tag[i]
            json_data = json.dumps(data)
            json_array.append(json_data)

        dictionary = []
        for j in json_array:
            dictionary.append(json.loads(j))

        df = pd.DataFrame(dictionary)
        with option_context('display.max_colwidth', 400):
            # display the dataframe
            print(df)


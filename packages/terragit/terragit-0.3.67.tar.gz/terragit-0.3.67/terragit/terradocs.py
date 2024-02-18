import gitlab
import os
import sys
import subprocess
from random import randrange

class terradoc:
    def __init__(self,git_url,gitlab_token , project_id):
        self.git_url =git_url
        self.gitlab_token =gitlab_token
        self.project_id=project_id
        self.module=False
        self.live=False

    def docs(self , module , live):
        gl = gitlab.Gitlab(self.git_url,private_token = self.gitlab_token)
        project = gl.projects.get(self.project_id)
        gitUrlToClone =project.ssh_url_to_repo
        subprocess.call(['git', 'clone', gitUrlToClone] ,)

        projectpath=os.getcwd()
        os.chdir(projectpath+"/"+project.name.lower() )
        if module == True and live == False:
            random_suffix=randrange(0, 1000)
            os.environ['BRANCH_NAME'] = "docs"+str(random_suffix)
            commands = [ #instal Graphviz
               'curl -Lo ./terraform-docs.tar.gz https://github.com/terraform-docs/terraform-docs/releases/download/v0.15.0/terraform-docs-v0.15.0-$(uname)-amd64.tar.gz',
               'tar -xzf terraform-docs.tar.gz' ,
               'chmod +x terraform-docs' ,
               'git checkout -b $BRANCH_NAME' ,
               'terraform-docs markdown table --output-file README.md --output-mode inject .',
               'terraform init &&terraform graph |  sed -n \'/digraph/,$p\' | dot -Tsvg > graph.svg' ,
               'git add ./README.md' ,
               'git add ./graph.svg',
               'git commit --allow-empty -m "add docs"',
               'git push -u origin $BRANCH_NAME -o merge_request.create -o merge_request.target=master -o merge_request.title="add docs" -o merge_request.description="add docs" -o merge_request.remove_source_branch=true -o merge_request.merge_when_pipeline_succeeds=false']
        if module ==False and live ==True:
            random_suffix=randrange(0, 1000)
            os.environ['BRANCH_NAME'] = "graph"+str(random_suffix)
            commands = [ #instal Graphviz
               'git checkout -b $BRANCH_NAME' ,
               'terragrunt graph-dependencies |  sed -n \'/digraph/,$p\' | dot -Tsvg > graph.svg' ,
               'git add ./graph.svg',
               'git commit --allow-empty -m "add graph"',
               'git push -u origin $BRANCH_NAME -o merge_request.create -o merge_request.target=master -o merge_request.title="add graph" -o merge_request.description="add graph" -o merge_request.remove_source_branch=true -o merge_request.merge_when_pipeline_succeeds=false']

        count = 0
        for com in commands:
            os.system(com)
            count += 1
        else:
            print ("Finish..")









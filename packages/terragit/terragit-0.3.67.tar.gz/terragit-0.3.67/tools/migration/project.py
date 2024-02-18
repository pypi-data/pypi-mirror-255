
from importlib.resources import path
import gitlab
import git
import os
import shutil
import glob
import subprocess
from tokenize import group
from variables_environnements import copy_variables_environnements_projects
from tf_state import getStates


#variables
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='****************')
gl_dest = gitlab.Gitlab(url='https://gitlab.allence.cloud',private_token='************')

def copy_project(project_id_source,groupId):
    os.mkdir("/tmp/gitlab")
    os.chdir("/tmp/gitlab")
    os.mkdir("projectSource")
    os.mkdir("projectDestination")

    project = gl_source.projects.get(project_id_source)
    print(project)
    projectDes = gl_dest.projects.create({'name': project.path, 'namespace_id': groupId})
    #print(projectDes)
    copy_variables_environnements_projects(project_id_source,projectDes.id)


    os.chdir("/tmp/gitlab/projectSource")
    subprocess.call(["git", "clone", "--origin", "origin", "--progress", "-v", project.ssh_url_to_repo])
    os.chdir("/tmp/gitlab/projectDestination")
    project2 = gl_dest.projects.get(projectDes.id)
    subprocess.call(["git", "clone", "--origin", "origin", "--progress", "-v", project2.ssh_url_to_repo])
    os.chdir("/tmp/gitlab/projectDestination/"+project2.path)
    #x = "/tmp/gitlab/projectDestination/"+project2.name+"/README.md"
    x2 = "/tmp/gitlab/projectSource/"+project.path+"/.git"
    #subprocess.call(["rm", x])
    shutil.rmtree(x2)
    path1 ="/tmp/gitlab/projectSource/"+project.path+"/."
    path2 ="/tmp/gitlab/projectDestination/"+project2.path+"/"
    subprocess.call(["cp", "-a", path1, path2])
    os.chdir("/tmp/gitlab/projectDestination/"+project2.path)
    subprocess.call(["git", "add", "."])
    subprocess.call(["git", "commit", "-m", "delete README.md"])
    subprocess.call(["git", "push"])
    shutil.rmtree("/tmp/gitlab")

    getStates(project.path_with_namespace,project.id,projectDes.id,"")


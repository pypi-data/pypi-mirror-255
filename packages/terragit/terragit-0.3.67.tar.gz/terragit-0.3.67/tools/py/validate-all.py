import sys
from os import listdir
from os.path import isdir, join
import gitlab
import os
import pathlib
import subprocess
import shutil

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m' 
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
pathList=[]
failedloglist=[]
logsFolder=""
printLogs=False

def tg_plan(path,logsFolder,printLogs):
    if  path in pathList:
        return
    else:
        pathList.append(path)
        only_tf_files=[f for f in  sorted(listdir(path)) if not isdir(join(path, f)) and f.endswith('.tf')]
        if len(only_tf_files)==0:
            onlyDirectories = [d for d in sorted(listdir(path)) if isdir(join(path, d)) and d !=".terraform" and d != ".terragrunt-cache"]
            if(len(onlyDirectories) > 0):
                for i in range(0, len(onlyDirectories)):
                    tg_plan(path+"/"+onlyDirectories[i],logsFolder,printLogs)
            return
        os.chdir(path)
        logfileName=path.split("live/")[1].replace("/","_")

        state_list = ("terragrunt validate -no-color 2>&1 | tee " +logsFolder+"/"+logfileName+".log")
        popen = subprocess.Popen(state_list, stdout = subprocess.PIPE, shell = True, encoding = 'utf8',env=os.environ.copy())
        lines = popen.stdout.readlines()
        popen.stdout.close()
        print(bcolors.OKBLUE+path+":" +bcolors.ENDC)
        for line in lines:
            if (printLogs):
                 print(line)
            else:
                if ("Error" in line):
                    lint=lines[(lines.index(line)):(len(lines))]
                    for l in lint:
                        print(l.replace('\n',''))
                    failedloglist.append(path)
                    print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
                    return
            if("Success! The configuration is valid" in line):
                print(bcolors.OKGREEN +"Success."+ bcolors.ENDC)
                return
        print(bcolors.FAIL +"configuration is not valid."+ bcolors.ENDC)
        failedloglist.append(path)


git_url="https://gitlab.allence.cloud"
if len(sys.argv) > 1:
    git_url = sys.argv[1]


logsFolder=pathlib.Path("logs").absolute().as_posix()
failedlogsFolder=pathlib.Path("failedlogs").absolute().as_posix()
idMr = os.environ.get('CI_MERGE_REQUEST_IID')
idProject=os.environ.get('CI_PROJECT_ID')
gitlab_token=os.environ.get('gitlab_token')
ci_commit_title=os.environ.get('CI_COMMIT_TITLE')
gl = gitlab.Gitlab(git_url,private_token = gitlab_token)
project = gl.projects.get(idProject)
mr= project.mergerequests.get(idMr)
folderList=[]
mrchange=mr.changes()
changes = mrchange['changes']
if (len(changes)==0):
    if not isdir(pathlib.Path(ci_commit_title).absolute().as_posix()):
        print(bcolors.FAIL+ci_commit_title+" is not valid path" + bcolors.ENDC)
        failedloglist.append(ci_commit_title)
    else:
        ci_mr_titlePath=pathlib.Path(ci_commit_title).absolute().as_posix()
        printLogs=True
        tg_plan(ci_mr_titlePath,logsFolder,printLogs)
else:
    for change in changes:
        newPath=change['new_path']
        if not ("live/") in newPath:
            print(pathlib.Path(newPath).absolute().as_posix()+bcolors.WARNING +" OUT of SCOPE"+ bcolors.ENDC)
        else:
            pathh=pathlib.Path(newPath).parent.absolute().as_posix()
            folderList.append(pathh)
mylist = list(dict.fromkeys(folderList))
TG_OUTPUT_LIMIT =3
if os.environ.get("TG_OUTPUT_LIMIT")!=3 and os.environ.get("TG_OUTPUT_LIMIT")!=None :
    TG_OUTPUT_LIMIT = os.environ.get("TG_OUTPUT_LIMIT")

if len(mylist)<=int(TG_OUTPUT_LIMIT) and any(".hcl" in l for l in mylist):
    printLogs=True
for path in mylist:
    if isdir(path):
        tg_plan(path,logsFolder,printLogs)
if failedloglist:
    for message in failedloglist:
        logfileName=message.split("live/")[1].replace("/","_")
        os.chdir(failedlogsFolder)
        shutil.move(logsFolder+"/"+logfileName+".log", "failed_"+logfileName+".log")
    sys.exit(1)

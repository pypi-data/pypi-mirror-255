import os
from os import listdir
from os.path import isdir, join
import subprocess
import sys
import shutil
import pathlib

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


def tg_plan(path,logsFolder):
    only_tf_files=[f for f in  sorted(listdir(path)) if not isdir(join(path, f)) and f.endswith('.tf')]
    if len(only_tf_files)==0:
        onlyDirectories = [d for d in sorted(listdir(path)) if isdir(join(path, d)) and d !=".terraform" and d != ".terragrunt-cache"]
        if(len(onlyDirectories) > 0):
            for i in range(0, len(onlyDirectories)):
                tg_plan(path+"/"+onlyDirectories[i],logsFolder)
        return

    os.chdir(path)
    logfileName=path.split("live/")[1].replace("/","_")
    state_list = ("terragrunt plan -no-color 2>&1 | tee " +logsFolder+"/"+logfileName+".log")
    popen = subprocess.Popen(state_list, stdout = subprocess.PIPE, shell = True, encoding = 'utf8')

    lines = popen.stdout.readlines()
    popen.stdout.close()
    print(bcolors.OKBLUE+path+":" +bcolors.ENDC)
    for line in lines:
        if("No changes. Infrastructure is up-to-date." in line):
            print(bcolors.OKGREEN +"  : No changes. Infrastructure is up-to-date."+ bcolors.ENDC)
            return
        if("Plan:" in line):
            print(bcolors.WARNING +line+ bcolors.ENDC)
            return
        if ("will be updated in-place" in line):
            print(line.replace('\n',''))
        if ("will be created" in line):
            print(line.replace('\n',''))
        if ("must be replaced" in line):
            print(line.replace('\n',''))

            lint=lines[(lines.index(line)):(len(lines))]
            lin=lint[0:(lint.index('\n'))]
            for l in lin:
                if ("forces replacement" in l):
                    print(l.replace('\n',''))
                    print(lin[(lin.index(l))+1])
        if ("will be destroyed" in line):
            print(line.replace('\n',''))
        if (line.startswith("Error")):
            lint=lines[(lines.index(line)):(len(lines))]
            for l in lint:
                print(l.replace('\n',''))
            print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
            failedloglist.append(path)
            return
    print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
    failedloglist.append(path)

rootPath = sys.argv[1]
failedloglist=[]
logsFolder=pathlib.Path("logs").absolute().as_posix()
failedlogsFolder=pathlib.Path("failedlogs").absolute().as_posix()

tg_plan(rootPath,logsFolder)

if failedloglist:
    for message in failedloglist:
        logfileName=message.split("live/")[1].replace("/","_")
        os.chdir(failedlogsFolder)
        shutil.move(logsFolder+"/"+logfileName+".log", "failed_"+logfileName+".log")
    sys.exit(1)


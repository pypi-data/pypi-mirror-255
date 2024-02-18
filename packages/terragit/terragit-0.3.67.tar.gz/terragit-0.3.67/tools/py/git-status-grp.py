import os
import sys

def status_projects(path):
    if os.path.isdir(path+'.git'):
        #print(path+" is a git repo")
        cmd = "cd "+path+ " && "+"git fetch "
        stream = os.popen(cmd)
        lines = stream.readlines()
        cmd = "cd "+path+ " && "+"git status "
        stream = os.popen(cmd)
        lines = stream.readlines()
        if len(lines) == 0 or "Your branch is up to date" in lines[1]:
            True
            #print(path + lines[1])
        else :
            print("#### "+path + " "+str(len(lines)))
            #for line in lines:
            #    print(line.rstrip("\n"))
            #print("###DEBUG")
            if "Your branch is behind" in lines[1]:
                print("#### branch is behind, so we are Pulling")
                cmd = "cd "+path+ " && "+ "git pull "
                os.popen(cmd)
            if "Changes to be committed" in lines[3]:
                print("#### Changes to be committed !!!")
                for line in lines:
                    print(line.rstrip("\n"))
            print("#### END")
            #else :
            #    for line in lines:
            #        line = line.rstrip("\n")
            #        print(line)
            #    exit()
    else :
        #print(path+" is not a git repo")
        for name in os.listdir(path) :
            if os.path.isdir(path+name+"/"):
                status_projects(path+name+"/")


path = sys.argv[1]
status_projects(path)

import os
import subprocess
class ProjectStatus:
    def __init__(self, colors):
        self.colors = colors

    def gitstatus(self, dirs):
        for dirpath, dirnames, filenames in os.walk(dirs):
            if self.is_git_workdir_or_repo(dirpath, dirnames, filenames):
                verif = 0
                cmd = "cd " + dirpath + " && git status"
                popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                         encoding='utf8')
                lines = popen.communicate(input='\n')[0].split("\n")
                for line in lines:
                    if ("nothing to commit, working tree clean" in line):
                        print(self.colors.OKGREEN + "nothing to commit in " + dirpath + " project")
                        verif = 1
                        break
                if verif == 0:
                    print(self.colors.WARNING + "you have uncommitted changes " + dirpath + " project")

    def is_git_workdir_or_repo(self, dirpath, dirnames, filenames):
        if (".git" in dirnames or ".git" in filenames) and (".terraform" not in dirpath):
            return 1
        return 0

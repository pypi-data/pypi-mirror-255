import shutil
import subprocess
import json
import requests
from terragit.terragrunt import *
import gitlab

logsFolder = ""
pathList = []
failedloglist = []
notif_paths = []
printLogs = False


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class apply_changes:
    def __init__(self):
        self.bcolor = bcolors

    def apply_ci(self):
        git_url = f"https://{os.environ.get('CI_SERVER_HOST')}"
        logsFolder = pathlib.Path("logs").absolute().as_posix()
        idProject = os.environ.get("CI_PROJECT_ID")
        idCommit = os.environ.get("CI_COMMIT_SHA")
        gitlab_token = os.environ.get("gitlab_token")
        ci_commit_title = os.environ.get("CI_COMMIT_TITLE")

        gl = gitlab.Gitlab(url=git_url, private_token=gitlab_token)
        project = gl.projects.get(idProject)
        commit = project.commits.get(idCommit)
        diff = commit.diff()
        folderList = []

        if len(diff) == 0:
            if not isdir(pathlib.Path(ci_commit_title).absolute().as_posix()):
                print(
                    bcolors.FAIL
                    + ci_commit_title
                    + " is not valid path "
                    + bcolors.ENDC
                )
            else:
                ci_commit_titlePath = (
                    pathlib.Path(ci_commit_title).absolute().as_posix()
                )
                printLogs = True
                self.apply(ci_commit_titlePath, logsFolder, printLogs)
        else:
            for change in diff:
                newPath = change["new_path"]
                notif_paths.append(newPath)
                if not ("live/") in newPath:
                    print(
                        pathlib.Path(newPath).absolute().as_posix()
                        + bcolors.WARNING
                        + " OUT of SCOPE"
                        + bcolors.ENDC
                    )
                else:
                    pathh = pathlib.Path(newPath).parent.absolute().as_posix()
                    folderList.append(pathh)
        mylist = list(dict.fromkeys(folderList))
        TG_OUTPUT_LIMIT = 3
        if (
            os.environ.get("TG_OUTPUT_LIMIT") != 3
            and os.environ.get("TG_OUTPUT_LIMIT") != None
        ):
            TG_OUTPUT_LIMIT = os.environ.get("TG_OUTPUT_LIMIT")
        if len(mylist) <= int(TG_OUTPUT_LIMIT):
            printLogs = True
        failedlogsFolder = pathlib.Path("failedlogs").absolute().as_posix()
        for path in mylist:
            if isdir(path):
                self.apply(path, logsFolder, printLogs)
        if failedloglist:
            for message in failedloglist:
                logfileName = message.split("live/")[1].replace("/", "_")
                os.chdir(failedlogsFolder)
                shutil.move(
                    logsFolder + "/" + logfileName + ".log",
                    "failed_" + logfileName + ".log",
                )
            sys.exit(1)

    def apply(self, path, logsFolder, printLogs):
        if path in pathList:
            return
        else:
            pathList.append(path)
            only_tf_files = [
                f
                for f in sorted(listdir(path))
                if not isdir(join(path, f)) and f.endswith(".tf")
            ]
            if len(only_tf_files) == 0:
                onlyDirectories = [
                    d
                    for d in sorted(listdir(path))
                    if isdir(join(path, d))
                    and d != ".terraform"
                    and d != ".terragrunt-cache"
                ]
                if len(onlyDirectories) > 0:
                    for i in range(0, len(onlyDirectories)):
                        self.apply(
                            path + "/" + onlyDirectories[i], logsFolder, printLogs
                        )
                return
            os.chdir(path)
            logfileName = path.split("live/")[1].replace("/", "_")
            state_list = (
                f"terragrunt apply -no-color 2>&1 | tee {logsFolder}/{logfileName}.log"
            )
            popen = subprocess.Popen(
                state_list, stdout=subprocess.PIPE, shell=True, encoding="utf8"
            )
            lines = popen.stdout.readlines()
            popen.stdout.close()
            print(bcolors.OKBLUE + path + ":" + bcolors.ENDC)

            for line in lines:
                if printLogs:
                    print(line)
                if "Error" in line:
                    lint = lines[(lines.index(line)) : (len(lines))]
                    for l in lint:
                        print(l.replace("\n", ""))
                    print(
                        bcolors.FAIL
                        + " COULDNT PROCESS , Terraform apply failed. Fix errors and run the script again!"
                    )
                    failedloglist.append(path)
                    break

                if "Apply complete! Resources:" in line:
                    print(bcolors.OKGREEN + line + bcolors.ENDC)
                    discord_api = os.environ.get("DISCORD_API")
                    var = self.user()
                    if discord_api != None:
                        payload = {"content": f"{line} for user {var} in {notif_paths}"}
                        json_message = json.dumps(payload, indent=4)
                        headers = {"Content-Type": "application/json; charset=UTF-8"}
                        requests.post(discord_api, data=json_message, headers=headers)
                    else:
                        print(
                            self.bcolor.WARNING
                            + " You haven't set yet your webhook for your group "
                        )
                    continue

    def user(self):
        state_list = 'aws sts get-caller-identity --query "Arn" --output text'
        popen = subprocess.Popen(
            state_list, stdout=subprocess.PIPE, shell=True, encoding="utf8"
        )
        lines = popen.stdout.readlines()
        return lines[0]

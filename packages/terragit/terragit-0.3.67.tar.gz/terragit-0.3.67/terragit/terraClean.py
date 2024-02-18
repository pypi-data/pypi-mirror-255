from terragit.gitlabFunctions import *
from datetime import datetime, timedelta
import terragit.terragrunt as terragrunt
from math import *



class TerraClean:
    def __init__(self, gitlab_token, git_url, ):
        self.bcolor = terragrunt.bcolors
        self.gitlab_functions = GitlabFunctions(gitlab_token, git_url)

    def clean(self, group_id, project_id, time, mr, branches):
        if project_id is not None:
            if branches == 'true':
                self.get_project_branches(project_id, time)
                return
            elif mr:
                self.clean_mrs(project_id, group_id, time)
                return
        elif group_id is not None:
            if branches == 'true':
                projects = []
                branches_to_delete = []
                page = 1
                per_page = 40
                while per_page == 40:
                    projects = projects + self.gitlab_functions.get_projects_of_group(group_id, page, per_page)
                    page = page + 1
                    per_page = len(projects)
                for project in projects:
                    branches_to_delete = branches_to_delete + self.get_project_branches(project['id'], time, "grp")
                self.delete_branches(branches_to_delete)
            elif mr == 'true':
                self.clean_mrs(project_id, group_id, time)

    def get_project_branches(self, project_id, time, param=""):
        branches = self.gitlab_functions.get_all_project_branches(project_id)

        branches_to_delete = []
        for br in branches:
            if 'commit' in br:
                commit_date = br['commit']['committed_date']
                commit_date = commit_date[0:commit_date.index('T')]
                datetime_object = datetime.strptime(commit_date, '%Y-%m-%d')
                commit_time_in_days = (datetime.utcnow() - datetime_object).days
                merged = ""
                if (commit_time_in_days >= time) and not (br["protected"]) and (br["merged"]):
                    print(
                        self.bcolor.WARNING + "branch " + br["name"] + " is outdated by " + str(commit_time_in_days) +
                        " and it has been merged but not deleted its web_url is: " + br["web_url"])
                    br["project_id"] = project_id
                    branches_to_delete.append(br)
                elif (commit_time_in_days >= time) and not (br["protected"]) and not br["merged"]:
                    print(self.bcolor.WARNING + "last commit in branch " + br["name"] +
                          " it has been created " + str(commit_time_in_days) + " days ago, its web_url is: " + br[
                              "web_url"])
                    br["project_id"] = project_id
                    branches_to_delete.append(br)
                elif (commit_time_in_days >= time) and (br["protected"]) and br["merged"]:
                    br["project_id"] = project_id
                    branches_to_delete.append(br)
                    print(self.bcolor.WARNING + "branch " + br["name"] +
                          " has been merged but not deleted its web_url is: " + br["web_url"])
        if param == "grp":
            return branches_to_delete
        else:
            self.delete_branches(branches_to_delete)

    def delete_branches(self, branches_to_delete):
        if len(branches_to_delete) == 0:
            print(self.bcolor.OKGREEN, "project is clean")
            return
        value = input(self.bcolor.OKBLUE + "would you like to delete all these branches at once, delete "
                                           "one by one or cancel clean operation ?[all/oneByOne/cancel]")
        if value == "all":
            for br in branches_to_delete:
                self.gitlab_functions.delete_branch(br["project_id"], br["name"])
        elif value == "oneByOne":
            for br in branches_to_delete:
                if input(self.bcolor.OKBLUE + "would you like to delete ths branch " +
                         br["name"] + " ?[yes/no]") == "yes":
                    self.gitlab_functions.delete_branch(br["project_id"], br["name"])

    def clean_mrs(self, project_id, group_id, time):
        created_before = datetime.now() - timedelta(days=time)
        created_before = created_before.strftime("%Y-%m-%dT%H:%M:%SZ")
        mrs_to_delete = []

        if project_id is not None:
            first_mrs = len(self.gitlab_functions.get_number_merge_request_project(project_id, created_before, 20, 1))

            if first_mrs == 20:
                count = first_mrs
                i = 1
                somme = 20
                while count % 20 == 0:
                    i += 1
                    other_mrs_count_intermidate= len(self.gitlab_functions.get_number_merge_request_project(project_id, created_before, 20, i))
                    somme += other_mrs_count_intermidate
                    if other_mrs_count_intermidate != 20:
                        break
            else:
                somme = 5

            a = ceil(somme / 20)
            for i in range(1, a+1):
                mrs_to_delete.insert(i-1, self.gitlab_functions.get_all_merge_request_by_page(project_id, created_before, i))

        elif group_id is not None:
            first_mrs = len(self.gitlab_functions.get_number_merge_request_group(group_id, created_before, 20, 1))

            if first_mrs == 20:
                count = first_mrs
                i = 1
                somme = 20
                while count % 20 == 0:
                    i += 1
                    other_mrs_count_intermidate = len(self.gitlab_functions.get_number_merge_request_group(group_id , created_before, 20, i))
                    somme += other_mrs_count_intermidate
                    if other_mrs_count_intermidate != 20:
                        break
            else:
                somme = 5
            a = ceil(somme / 20)
            for i in range(1, a+1):
                mrs_to_delete.insert(i-1, self.gitlab_functions.get_all_group_merge_requests_per_page(group_id, created_before, i))

        if len(mrs_to_delete[0]) == 0:
            print(self.bcolor.OKGREEN, "project is clean")

        else:

            for i in range(0, len(mrs_to_delete)):
                for j in range(0, len(mrs_to_delete[i])):
                    print(self.bcolor.WARNING + "Merge request " + mrs_to_delete[i][j]["title"] + " is created before " + str(
                        created_before))
                value = input(self.bcolor.OKBLUE + "would you like to delete all these merge requests at once, delete "
                                                    "one by one or cancel clean operation ?[all/oneByOne/cancel]")

        if value == "all":
            for i in range(0, len(mrs_to_delete)):
                for j in range(0, len(mrs_to_delete[i])):
                    self.gitlab_functions.update_mr_state(mrs_to_delete[i][j]["project_id"], mrs_to_delete[i][j]["iid"])
        elif value == "oneByOne":
            for i in range(0, len(mrs_to_delete)):
                for j in range(0, len(mrs_to_delete[i])):
                    if input(self.bcolor.OKBLUE + "would you like to delete this merge requests " +
                             mrs_to_delete[i][j]["title"] + " ?[yes/no]") == "yes":
                        self.gitlab_functions.update_mr_state(mrs_to_delete[i][j]["project_id"], mrs_to_delete[i][j]["iid"])

        elif value == "cancel":
            return
        print(self.bcolor.OKGREEN, "project has been cleaned successfully")

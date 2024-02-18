import argparse
import os
import sys

import terragit.addUserGitlabRepo as add_user_gitlab_repository
import terragit.clone as clone
import terragit.comapare as compare
import terragit.gitlabFunctions as GitlabFunctions
import terragit.projectStatus as ProjectStatus
import terragit.terraClean as terraClean
import terragit.terraConf as terra_conf
import terragit.terracommand as terracommande
import terragit.terradocs as terradocse
import terragit.terragrunt as terragrunt
import terragit.utilsFunctions as utils
import terragit.terraValidate as terraValidate
import terragit.mrchanges as mrchanges
import terragit.apply as applychanges
import terragit.terraStatus as terraStatus
import terragit.createGroup as creation
import terragit.ValidateCi as validation


def main():

    parser = argparse.ArgumentParser()
    colors = terragrunt.bcolors()
    terraconf = terra_conf.TerraConf()
    parser.add_argument("-u", "--gitlab_url", dest="gitlab_url", default="https://gitlab.allence.cloud", help="gitlab url")
    verif = terraconf.verif_file_and_credentials_existence()
    token_ci_id = os.getenv("CI_JOB_TOKEN")
    if token_ci_id is None:
        if (sys.argv[1] in ["config"]) or (verif != "false"):
            if sys.argv[1] == "config":
                terraconf.init_file()

            if sys.argv[1] == "clone":

                parser.add_argument("-g", "--group_id", dest="group_id", default=None, help="group id")
                parser.add_argument("-p", "--project_id", dest="project_id", default=None, help="id of project")
                parser.add_argument("-ip", "--infra_project_id", dest="infra_project_id",
                                    default=None, help="id of the infrastructure project")
                parser.add_argument("-path", "--path", dest="path", default="./",
                                    help="path in which the project will be cloned")

                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                print(colors.OKCYAN, "Cloning ...")

                clonn = clone.Clone(verif["gitlab_token"], verif["gitlab_url"], args.path)

                clonn.clone_projects(args.project_id, args.group_id , args.path)
                # print(colors.OKCYAN, "Checking the existance of IAM user ...")
                # utilsFunctions = utils.UtilsFunctions(verif["gitlab_token"], args.gitlab_url)
                # gt = GitlabFunctions.GitlabFunctions(verif["gitlab_token"], args.gitlab_url)
                # service_path = utilsFunctions.check_content_existance_in_serviceGr(args.group_id,args.infra_project_id,
                #                                                                    'https://git@gitlab.com/commons-acp/terraform/aws/user.git','name="' + verif["gitlab_user"] + '"')
                #
                # if "content_found" in service_path:
                #     print(colors.OKGREEN, "IAM user found!")
                #
                #     terraconf.add_credentials_to_group(args.gitlab_url, verif["gitlab_token"], args.group_id,
                #                                        args.infra_project_id, args.path, "/"+service_path[29:service_path.rindex("/")], "true")
                # else:
                #     print("iam user not found")
                #     terraconf.add_credentials_to_group(args.gitlab_url, verif["gitlab_token"],args.group_id,
                #                                        args.infra_project_id, args.path, "", "false")

            if sys.argv[1] == "adduser":
                parser.add_argument("-g", "--group_id", dest="group_id", default=None, help="group id")
                parser.add_argument("-p", "--project_id", dest="project_id", default=None,
                                    help="id of infrastructure project")
                parser.add_argument("-gu", "--gitlab_username", dest="gitlab_username", default=None,
                                    help="member gitlab username")
                parser.add_argument("-lvl", "--access_level", dest="access_level", default=None,
                                    help="User access level can be guest, reporter, developer, maintainer or owner")
                # parser.add_argument("-k", "--keybase_username", dest="keybase_username", default=None,
                #                     help="user keybase username")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                add_user_gitlab_repo = add_user_gitlab_repository.AddUserGitlabRepo(verif["gitlab_token"], args.gitlab_url)

                exist = add_user_gitlab_repo.existance_gitlab(args.project_id, args.group_id, args.gitlab_username)
                if exist[0] == 'user exist in gitlab project & ':
                    print(colors.FAIL + "user exist in gitlab project")
                else:
                    add_user_gitlab_repo.add_user_repository(args.project_id, args.group_id, args.gitlab_username, args.access_level,
                                                             exist)

            if sys.argv[1] == "project-list":
                parser.add_argument("-dir", "--directory", dest="directory", default=None, help="local path to clone group")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                list = clone.Clone('glpat-BS_yy1VSPx2PKkbjokN3', 'https://gitlab.allence.cloud/', '')
                list.list_project(args.directory)

            if sys.argv[1] == "switch":
                parser.add_argument("-g", "--group_id", dest="group_id", default=None, help="gitlab group id")
                parser.add_argument("-gn", "--group_name", dest="group_name", default=None, help="gitlab group name")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                content = terraconf.get_file_content()
                terraconf.switch_project(content, args.group_id, args.group_name)

            if sys.argv[1] == "aws-adduser":
                group_id = os.getenv("GROUP_ID")
                parser.add_argument("-gu", "--gitlab_username", dest="gitlab_username", default=None,
                                    help="member gitlab username")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                add_user_aws = utils.UtilsFunctions(verif["gitlab_token"], args.gitlab_url)
                add_user_aws.add_aws_account(group_id, args.gitlab_username)

            if sys.argv[1] == "docs":
                parser.add_argument("-m", "--module", action="store_true", help="module")
                parser.add_argument("-l", "--live", action="store_true", help="live")
                parser.add_argument("-o", "--output", dest="output_path", default="./", help="output path")
                parser.add_argument("-p", "--project_id", dest="project_id", default=None, help="id of project")
                parser.add_argument(sys.argv[1])

                args = parser.parse_args()
                terradoc = terradocse.terradoc(args.gitlab_url, verif["gitlab_token"], args.project_id)
                terradoc.docs(args.module, args.live)

            if sys.argv[1] == "plan":

                parser.add_argument("-gn", "--group_name", dest="group_name", default=None,
                                    help="your group name")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                order = terracommande.terracommand("","","","","","","","")
                order.terragrunt_plan(args.group_name)

            if sys.argv[1] == "create-group":
                parser.add_argument("-gn", "--group_name", dest="group_name", default=None,
                                    help="your group name")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                group_creation = creation.Create()
                group_creation.create_group(args.group_name)
            ####
            if sys.argv[1] == "compare":
                print("comparing infra")
                parser.add_argument("-I", "--infra", dest="infra", default=None, help="path to infra")
                parser.add_argument("-N", "--infra2", dest="infra2", default=None, help="path to infra")
                parser.add_argument(sys.argv[1])


                args = parser.parse_args()
                list = compare.Compare(verif["gitlab_token"], args.gitlab_url)
                #
                list.compare_tf_states(args.infra, args.infra2)

            if sys.argv[1] == "validate":
                print("argv", sys.argv)
                print("validate infra")
                parser.add_argument("-p", "--path_local", dest="local_path", default=None, help="local path to infra")
                parser.add_argument("-P", "--path", dest="path", default=None, help="path to infra")
                parser.add_argument("-prId", "--project_id", dest="project_id", help="project id")
                parser.add_argument(sys.argv[1])

                args = parser.parse_args()
                list = terraValidate.TerraValidate(verif["gitlab_token"], args.gitlab_url)
                if(sys.argv[2] == "-p"):
                    list.validate_projects(args.local_path)
                else:
                    list.validate_distant(args.project_id, args.path)

            if sys.argv[1] == "list":
                content = terraconf.get_file_content()
                terraconf.list_projects(content)

            if sys.argv[1] == "currentProject":
                content = terraconf.get_file_content()
                terraconf.get_selected_project(content)

            if sys.argv[1] == "clean":
                parser.add_argument("-g", "--group_id", dest="group_id", default=None, help="gitlab group id")
                parser.add_argument("-p", "--project_id", dest="project_id", default=None, help="gitlab project id")
                parser.add_argument("-t", "--time", dest="time", default=90, help="provide time to delete "
                                                                                  "branches/merge-requests older then time provided")
                parser.add_argument("-mr", "--mr", dest="mr", help="set it to true if you want to delete Mr else false")
                parser.add_argument("-b", "--branches", dest="branches", help="set it to true if you want to delete "
                                                                              "branches else false")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                terra_clean = terraClean.TerraClean(verif["gitlab_token"], args.gitlab_url)
                terra_clean.clean(args.group_id, args.project_id, int(args.time), args.mr, args.branches)

            if sys.argv[1] == "help":
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                util = utils.UtilsFunctions(verif["gitlab_token"], args.gitlab_url)
                util.help()

            if sys.argv[1] == "status":
                parser.add_argument("-dir", "--directory", dest="directory", default=None, help="gitlab path")
                parser.add_argument(sys.argv[1])
                args = parser.parse_args()
                status = ProjectStatus.ProjectStatus(colors)
                status.gitstatus(args.directory)

        else:
            print(colors.FAIL, "terragit is not initialised please run `terragit config` command first")

        if sys.argv[1] == "verify":
            parser.add_argument(sys.argv[1])
            util = utils.UtilsFunctions("", "")
            util.verify_before_hook()

    else:

        if sys.argv[1] == "plan":

            parser.add_argument("-gn", "--group_name", dest="group_name", default=None,
                                help="your group name")
            parser.add_argument(sys.argv[1])
            args = parser.parse_args()
            plan = mrchanges.mr_changes()
            plan.plan_ci()
        if sys.argv[1] == "apply":
            parser.add_argument("-gn", "--group_name", dest="group_name", default=None,
                                help="your group name")
            parser.add_argument(sys.argv[1])
            apply = applychanges.apply_changes()
            apply.apply_ci()

        if sys.argv[1] == "validate":
            validate = validation.Validate()
            validate.validate_ci()

        if sys.argv[1] == "status":
            parser.add_argument("-gn", "--group_name", dest="group_name", default=None,
                                help="your group name")
            parser.add_argument(sys.argv[1])
            status = terraStatus.Status()
            status.module()
        if sys.argv[1] == "notify":

            parser.add_argument("-m", "--message", dest="message", default=None,
                                help="your message")
            parser.add_argument(sys.argv[3])
            args = parser.parse_args()
            validate = validation.Validate()
            validate.terragit_notify(args.message)


if __name__ == '__main__':
    main()

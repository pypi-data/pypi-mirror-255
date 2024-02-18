import gitlab

#variables
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='***********************')

def deleteUsersProject(projectid):
    projet = gl_source.projects.get(projectid)
    members = projet.members_all.list(get_all=True)
    print("project")
    print(projet)
    for member in members:
        #print("delete"+member.username)
        if member.username == "walid.mansia":
            print("owner "+member.username)
        else:
            try:
                projet.members.delete(member.id)
                print("delete "+member.username)
            except:
                print("skip this step")



def deleteUsersGroup(groupid):
    groupe = gl_source.groups.get(groupid)
    members = groupe.members_all.list(get_all=True)
    print("group")
    print(groupe)
    for member in members:
        #print("delete"+member.username)
        if member.username == "walid.mansia":
            print("owner "+member.username)
        else:
            try:
                groupe.members.delete(member.id)
                print("delete "+member.username)
            except:
                print("skip this step")

#deleteUsersProject(18085463)
#deleteUsersGroup(7516055)
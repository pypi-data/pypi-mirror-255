import gitlab
from delete import deleteUsersProject
from delete import deleteUsersGroup



#variables
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='******************')




def groupRecursively(group_id,parent_id):

    #Source Group
    Globalgroup = gl_source.groups.get(group_id)
    print(Globalgroup.name)
    #print("token of old tokens: ",Globalgroup.runners_token)


    #Source SubGroups
    subGroups = gl_source.groups.get(group_id).subgroups.list(get_all=True)
    #print("subGroups",subGroups)

    #Source SubProjects
    projects = gl_source.groups.get(group_id).projects.list(get_all=True)
    #print("SubProjects",projects)


    #delete users Project
    for project in projects:
      if project.id==7701367 or project.id==15440120 or project.id==21149583 or project.id==18828733 or project.id==18828730 or project.id==17730866:
        print("project skipped")
      else:
           #print("do")
            deleteUsersProject(project.id)
    #delete users SubGroup
    for subGroup in subGroups:
        #print(subGroup.name)
        deleteUsersGroup(subGroup.id)
        groupRecursively(subGroup.id,None)

    deleteUsersGroup(group_id)


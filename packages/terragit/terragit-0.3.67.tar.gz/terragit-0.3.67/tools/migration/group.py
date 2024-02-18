import gitlab
from project import copy_project
from variables_environnements import copy_variables_environnements_groupes
from import_porjects import import_porjects


#variables
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='******************')
gl_dest = gitlab.Gitlab(url='https://gitlab.allence.cloud',private_token='*********')



def groupRecursively(group_id,parent_id):

    #Source Group
    Globalgroup = gl_source.groups.get(group_id)
    print(Globalgroup.name)
    #print("token of old tokens: ",Globalgroup.runners_token)



    #Create Group Destination
    if parent_id is None:
        groupo = gl_dest.groups.create({'name': Globalgroup.name, 'path': Globalgroup.path})
        copy_variables_environnements_groupes(Globalgroup.id,groupo.id)
        groups_tokens= gl_dest.groups.get(groupo.id)
        #print("token of new tokens: ",groups_tokens.runners_token)

    else:
        groupo = gl_dest.groups.create({'name': Globalgroup.name, 'path': Globalgroup.path, 'parent_id': parent_id})
        copy_variables_environnements_groupes(Globalgroup.id,groupo.id)
        groups_tokens= gl_dest.groups.get(groupo.id)
        #print("token of new tokens: ",groups_tokens.runners_token)
    #print(groupo.id)


    #Source SubGroups
    subGroups = gl_source.groups.get(group_id).subgroups.list(get_all=True)
    #print("subGroups",subGroups)

    #Source SubProjects
    projects = gl_source.groups.get(group_id).projects.list(get_all=True)
    #print("SubProjects",projects)


    #Create SubGroupe Project Destination
    for project in projects:
        copy_project(project.id,groupo.id)
        #import_porjects(project.id,groupo.full_path)

    #Create SubGroup
    for subGroup in subGroups:
        #print(subGroup.name)
        groupRecursively(subGroup.id,groupo.id)


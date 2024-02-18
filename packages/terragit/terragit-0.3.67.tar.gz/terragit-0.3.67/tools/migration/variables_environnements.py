import gitlab

#variables
#add gitlab api source
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='************')
#add gitlab api destination
gl_dest = gitlab.Gitlab(url='https://gitlab.allence.cloud',private_token='**************')



def copy_variables_environnements_projects(project_id_source,project_id_dest):
    project_source = gl_source.projects.get(project_id_source)
    variables_projects_source = project_source.variables.list(get_all=True)

    project_dest = gl_dest.projects.get(project_id_dest)
    variables_projects_dest = project_dest.variables.list(get_all=True)

    for v in variables_projects_source:
        vars_projects_source = project_source.variables.get(v.key)
        variables_projects_dist = project_dest.variables.create({'key': vars_projects_source.key, 'value': vars_projects_source.value,'variable_type': vars_projects_source.variable_type, 'protected': vars_projects_source.protected, 'masked': vars_projects_source.masked, 'environment_scope': vars_projects_source.environment_scope})


def copy_variables_environnements_groupes(groupe_id_source,groupe_id_dest):
    groupe_source = gl_source.groups.get(groupe_id_source)
    variables_groupes_source = groupe_source.variables.list(get_all=True)

    groupe_dest = gl_dest.groups.get(groupe_id_dest)
    variables_groupes_dest = groupe_dest.variables.list(get_all=True)

    for v in variables_groupes_source:
        vars_groupes_source = groupe_source.variables.get(v.key)
        variables_groupes_dist = groupe_dest.variables.create({'key': vars_groupes_source.key, 'value': vars_groupes_source.value,'variable_type': vars_groupes_source.variable_type, 'protected': vars_groupes_source.protected, 'masked': vars_groupes_source.masked, 'environment_scope': vars_groupes_source.environment_scope})

    
    

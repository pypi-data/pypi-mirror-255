import time

import gitlab
import os
from variables_environnements import copy_variables_environnements_projects
from tf_state import getStates



#variables
gl_source = gitlab.Gitlab(url='https://gitlab.com',private_token='************************')
gl_dest = gitlab.Gitlab(url='https://gitlab.normalyzr.com',private_token='*******************')

def import_porjects(project_id_source,path_with_namespace):

    project = gl_source.projects.get(project_id_source)
    print(project)
    #projectDes = gl_dest.projects.create({'name': project.path, 'namespace_id': groupId})

    export = project.exports.create()
    print(export)

    export.refresh()
    while export.export_status != 'finished':
        time.sleep(1)
        export.refresh()

    # Download the result
    with open('/tmp/export.tgz', 'wb') as f:
        export.download(streamed=True, action=f.write)

    with open('/tmp/export.tgz', 'rb') as f:
        output = gl_dest.projects.import_project(
            f,
            path=project.path,
            name=project.path,
            namespace=path_with_namespace,
        )
    project_import = gl_dest.projects.get(output['id'], lazy=True).imports.get()
    while project_import.import_status != 'finished':
        time.sleep(1)
        project_import.refresh()

    os.remove('/tmp/export.tgz')
    copy_variables_environnements_projects(project_id_source,project_import.id)
    getStates(project.path_with_namespace,project.id,project_import.id,"")
#import_porjects(33354189,'test')
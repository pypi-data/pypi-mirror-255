
import gitlab

#add gitlab api
gl_dest = gitlab.Gitlab(url='https://gitlab.allence.cloud',private_token='**************')
groups = gl_dest.groups.list()
#print(groups)
for group in groups:
    gl_dest.groups.delete(group.id)


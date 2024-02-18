from urllib import response
import requests
import json


def add_tf_state(name_tf_state,body,project_id_dest):
    headers = {
        'PRIVATE-TOKEN': '*************',
        'Content-Type': 'application/json'
    }
    id=str(project_id_dest)
    url = 'https://gitlab.normalyzr.com/api/v4/projects/'+id+'/terraform/state/'+name_tf_state

    response = requests.post(url,json=body, headers=headers)
    print(response.json())



def get_tf_state(name_tf_state,project_id_source):
    headers = {
        'PRIVATE-TOKEN': '********************',
        'Content-Type': 'application/json'
    }
    id =str(project_id_source)
    url = 'https://gitlab.com/api/v4/projects/'+id+'/terraform/state/'+ name_tf_state

    response = requests.get(url, headers=headers)
    return response.json()



def getStates(path_with_namespace,project_id_source,project_id_dest,endCursor):
    #after = ["","eyJuYW1lIjoiYXdzX3N1Yl9wcm9kXzgyMjg3NDUxMDI3N19wcm9qZWN0c195enJfYWlfZmlsZWJlYXQiLCJpZCI6IjI2OTg4MjAifQ","eyJuYW1lIjoibnMzMTI3MDMzLWlwLTUxLTY4LTM0LWV1X2lwMTY5LWlwLTUxLTE3OC0xNjgtZXVfc29uYXIiLCJpZCI6IjczODg5NSJ9"]
    #for i in after :
    #add source gitlab api
    headers = {
        'PRIVATE-TOKEN': '*************************',
        'Content-Type': 'application/json'
    }
    url = 'https://gitlab.com/api/graphql'
    body1 ={
        "operationName": "getStates",
        "query": "query getStates($projectPath: ID!, $first: Int, $last: Int, $before: String, $after: String) {\n  project(fullPath: $projectPath) {\n    id\n    terraformStates(first: $first, last: $last, before: $before, after: $after) {\n      count\n      nodes {\n        ...State\n        __typename\n      }\n      pageInfo {\n        ...PageInfo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment State on TerraformState {\n  id\n  name\n  lockedAt\n  updatedAt\n  deletedAt\n  lockedByUser {\n    ...User\n    __typename\n  }\n  latestVersion {\n    ...StateVersion\n    __typename\n  }\n  __typename\n}\n\nfragment User on User {\n  id\n  avatarUrl\n  name\n  username\n  webUrl\n  __typename\n}\n\nfragment StateVersion on TerraformStateVersion {\n  id\n  downloadPath\n  serial\n  updatedAt\n  createdByUser {\n    ...User\n    __typename\n  }\n  job {\n    id\n    detailedStatus {\n      id\n      detailsPath\n      group\n      icon\n      label\n      text\n      __typename\n    }\n    pipeline {\n      id\n      path\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PageInfo on PageInfo {\n  hasNextPage\n  hasPreviousPage\n  startCursor\n  endCursor\n  __typename\n}\n",
        "variables": {
            "after": endCursor,
            "first": 100,
            "projectPath": path_with_namespace
        }
    }
    #print (i)
    response1 = requests.get(url, json=body1, headers=headers)
    d1 = response1.json()
    print(d1)
    endCursor = d1['data']['project']['terraformStates']['pageInfo']['endCursor']

    #print(endCursor)
    array_nodes1 = d1['data']['project']['terraformStates']['nodes']
    print(array_nodes1)
    print(endCursor)
    if array_nodes1 is None:
        print("this project haven't tf_states")
    else:
        for tab in array_nodes1:
            #names1 = tab["name"]
            json1 = get_tf_state(tab["name"],project_id_source)
            #print(tab["name"])
            add_tf_state(tab["name"],json1,project_id_dest)
    if endCursor is None:
        print("less than 100 tf state")
    else:
        getStates(path_with_namespace,project_id_source,project_id_dest,endCursor)





#add_tf_state("aws_00-root-355748164128_cloudfront_dev_clearchannel_ocr",{'version': 4, 'terraform_version': '1.0.0', 'serial': 0, 'lineage': '9924aa36-c5ee-72f8-1087-fa5ce6ab6586', 'outputs': {}, 'resources': [{'module': 'module.cloudfront', 'mode': 'data', 'type': 'aws_region', 'name': 'main', 'provider': 'provider["registry.terraform.io/hashicorp/aws"].cloudfront', 'instances': [{'schema_version': 0, 'attributes': {'current': None, 'description': 'US East (N. Virginia)', 'endpoint': 'ec2.us-east-1.amazonaws.com', 'id': 'us-east-1', 'name': 'us-east-1'}, 'sensitive_attributes': []}]}, {'module': 'module.cloudfront', 'mode': 'managed', 'type': 'aws_acm_certificate', 'name': 'cert_app', 'provider': 'provider["registry.terraform.io/hashicorp/aws"].cloudfront', 'instances': [{'schema_version': 0, 'attributes': {'arn': 'arn:aws:acm:us-east-1:355748164128:certificate/52b7679d-e85b-4ed8-9f1f-aea544f2300b', 'certificate_authority_arn': '', 'certificate_body': None, 'certificate_chain': None, 'domain_name': 'ocr-dev-clearchannel.normalyzr.com', 'domain_validation_options': [{'domain_name': 'ocr-dev-clearchannel.normalyzr.com', 'resource_record_name': '_8daac544f74db72586992733ae50abf0.ocr-dev-clearchannel.normalyzr.com.', 'resource_record_type': 'CNAME', 'resource_record_value': '_8ab0a7318b4705e01e0b46fb90d741ac.fpktwqqglf.acm-validations.aws.'}], 'id': 'arn:aws:acm:us-east-1:355748164128:certificate/52b7679d-e85b-4ed8-9f1f-aea544f2300b', 'options': [{'certificate_transparency_logging_preference': 'ENABLED'}], 'private_key': None, 'status': 'PENDING_VALIDATION', 'subject_alternative_names': [], 'tags': None, 'validation_emails': [], 'validation_method': 'DNS'}, 'sensitive_attributes': [], 'private': 'bnVsbA=='}]}]},89)
#getStates("yzr-ai/projects/infrastructure/live/yzr-ai",33354189,439)
#get_tf_state("aws_00-root-355748164128_cloudfront_dev_clearchannel_ocr")
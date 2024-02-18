import os
import requests


output_file = "env_vars.sh"
if os.path.exists(output_file):
    os.remove(output_file)
def export_env_vars_from_vault(path):
    VAULT_TOKEN = "hvs.4ogyPJGV9Y9AEqNpBNAVmgdU"
    VAULT_ADDR = "https://vault.allence.cloud"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    print(path)
    url = f"{VAULT_ADDR}/v1/{str(path)}"
    print(url)
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]["data"]
        with open(output_file, "a") as script_file:
            # Iterate over the keys in the response data
            for key, value in data.items():
                # Export the key-value pair as environment variables
                os.environ[key] = value
                script_file.write(f"export {key}='{value}'\n")
                print(value)

    else:
        print(f"Failed to fetch secrets from Vault or no secrets in vault {path} . Status code: {response.status_code}")
def get_secrets_path(input_str):
    l=[]
    parts = input_str.strip('/').split('/')
    if 'builds' in parts:
        index = parts.index('builds')
        for i in range(index + 1, len(parts)):
            os.environ[f"{chr(ord('A') + i - index - 1)}"] = parts[i]
            l.append(parts[i])
    return l

input_str ="/builds/commons-acp/docker-images/terraform" #os.getenv("CI_PROJECT_DIR")

if len(get_secrets_path(input_str))==2:
    for var in ['A', 'B']:
        var=os.environ.get(var)
    GP=f"{os.environ.get('A')}/data/variables"
    export_env_vars_from_vault(GP)
    G1=f"{os.environ.get('A')}/data/{os.environ.get('B')}"
    export_env_vars_from_vault(G1)

elif len(get_secrets_path(input_str))==3:
    for var in ['A', 'B','C']:
        var=os.environ.get(var)
    GP=f"{os.environ.get('A')}/data/variables"
    export_env_vars_from_vault(GP)
    G1=f"{os.environ.get('A')}/data/{os.environ.get('B')}/variables"
    export_env_vars_from_vault(G1)
    G2=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}"
    export_env_vars_from_vault(G2)
elif len(get_secrets_path(input_str))==4:
    for var in ['A', 'B','C','D']:
        var=os.environ.get(var)
    GP=f"{os.environ.get('A')}/data/variables"
    export_env_vars_from_vault(GP)
    G1=f"{os.environ.get('A')}/data/{os.environ.get('B')}/variables"
    export_env_vars_from_vault(G1)
    G2=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}/variables"
    export_env_vars_from_vault(G2)
    G3=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}/{os.environ.get('D')}"
    export_env_vars_from_vault(G3)
elif len(get_secrets_path(input_str))==5:
    for var in ['A', 'B','C','D','E']:
        var=os.environ.get(var)
    GP=f"{os.environ.get('A')}/data/variables"
    export_env_vars_from_vault(GP)
    G1=f"{os.environ.get('A')}/data/{os.environ.get('B')}/variables"
    export_env_vars_from_vault(G1)
    G2=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}/variables"
    export_env_vars_from_vault(G2)
    G3=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}/{os.environ.get('D')}/variables"
    export_env_vars_from_vault(G3)
    G4=f"{os.environ.get('A')}/data/{os.environ.get('B')}/{os.environ.get('C')}/{os.environ.get('D')}/{os.environ.get('E')}"
    export_env_vars_from_vault(G4)
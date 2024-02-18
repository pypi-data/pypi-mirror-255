import os
import requests


output_file = "env_vars.sh"
if os.path.exists(output_file):
    os.remove(output_file)
def export_env_vars_from_vault(path):
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")
    VAULT_ADDR = "https://vault.allence.cloud"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    #print(path)
    url = f"{VAULT_ADDR}/v1/{str(path)}"
    print(url)
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]["data"]
        with open(output_file, "a") as script_file:
            for key, value in data.items():
                # Export the key-value from vault
                os.environ[key] = value
                script_file.write(f"export {key}='{value}'\n")

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

input_str = os.getenv("CI_PROJECT_DIR")
result = get_secrets_path(input_str)

if len(result) >= 2:
    char_list = [chr(65 + i) for i in range(len(result))]  # Generates ['A', 'B']
    base_path = f"{os.environ.get(char_list[0])}/data"
    path_parent_group=f"{os.environ.get(char_list[0])}/data/variables"
    print(path_parent_group)
    export_env_vars_from_vault(path_parent_group)
    for var in char_list[1:]:  # Start from the second element to exclude "commons-acp"
        base_path += f"/{os.environ.get(var)}"
        if var == char_list[len(char_list)-1]:
            print(base_path)
            export_env_vars_from_vault(base_path)
        else:
            print(base_path + "/variables")
            export_env_vars_from_vault(base_path + "/variables")



else:
    char_list = []

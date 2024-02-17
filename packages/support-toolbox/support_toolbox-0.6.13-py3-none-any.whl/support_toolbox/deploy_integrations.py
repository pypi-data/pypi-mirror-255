import requests
import json
import subprocess
import os
import configparser
from support_toolbox.utils.helper import select_api_url

# Get the path to the user's home directory
user_home = os.path.expanduser("~")

# Construct the full path to the configuration file
tokens_file_path = os.path.join(user_home, ".tokens.ini")

# Initialize the configparser and read the tokens configuration file
config = configparser.ConfigParser()
config.read(tokens_file_path)

# Read tokens/variables for the deploy_integrations tool
mt_api_token = config['deploy_integrations']['MT_API_TOKEN']

INTEGRATIONS = [
    "athena", "azure-synapse", "bigquery", "denodo",
    "ibm-db2", "infor-ion", "java-jdbc", "microsoft-sql-server",
    "mysql", "oracle-database", "postgresql",
    "python", "redshift", "snowflake"
]


def extract_integration(integration):
    os.environ["DW_AUTH_TOKEN"] = mt_api_token

    # Append the desired directory to the PATH temporarily for the subprocess call
    os.environ['PATH'] = os.pathsep.join([os.environ['PATH'], os.path.expanduser('~/.dw/cli/bin')])

    # Determine the path to Java 11 and set JAVA_HOME
    java_home_command = '/usr/libexec/java_home -v 11'
    java_home_output = subprocess.check_output(java_home_command, shell=True, text=True).strip()
    os.environ['JAVA_HOME'] = java_home_output

    command = f"bin/extract {integration}"

    directory_path = os.path.expanduser("~/integration-templates")

    # Execute the terminal command in the specified directory
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                cwd=directory_path)

    # Check the result
    if result.returncode == 0:
        print("Command executed successfully:")
        print(result.stdout)
    else:
        print("Command failed:")
        print(result.stderr)


def push_integration(api_url, integration, api_token):
    # Use VPC URLs here only
    vpc_urls = ["https://api.mckinsey.data.world/v0", "https://api.indeed.data.world/v0"]

    if api_url in vpc_urls:
        customer = api_url.split('.')[1]
        os.environ["DW_API_URL"] = f"api.{customer}.data.world"

    os.environ["DW_AUTH_TOKEN"] = api_token

    # Append the desired directory to the PATH temporarily for the subprocess call
    os.environ['PATH'] = os.pathsep.join([os.environ['PATH'], os.path.expanduser('~/.dw/cli/bin')])

    # Determine the path to Java 11 and set JAVA_HOME
    java_home_command = '/usr/libexec/java_home -v 11'
    java_home_output = subprocess.check_output(java_home_command, shell=True, text=True).strip()
    os.environ['JAVA_HOME'] = java_home_output

    command = f"bin/apply {integration}.template"

    directory_path = os.path.expanduser("~/integration-templates")

    # Execute the terminal command in the specified directory
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            cwd=directory_path)

    # Check the result
    if result.returncode == 0:
        print("Command executed successfully:")
        print(result.stdout)
    else:
        print("Command failed:")
        print(result.stderr)

    # Reset the DW_API_URL if exists
    if "DW_API_URL" in os.environ:
        del os.environ["DW_API_URL"]


def add_discoverable_to_integration(org, dataset_id, api_token, api_url):
    update_dataset = api_url + f"/datasets/{org}/{dataset_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    payload = {
        "visibility": "OPEN"
    }
    body = json.dumps(payload)

    # Update a specific dataset
    response = requests.patch(update_dataset, body, headers=header)

    # Verify the update
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
    else:
        print(response.text)


def deploy_integrations(api_url, api_token, selection):

    if selection == '1':
        # Deploy all specific integrations in the INTEGRATIONS list
        for integration_name in INTEGRATIONS:
            push_integration(api_url, integration_name, api_token)
            add_discoverable_to_integration("datadotworld-apps", integration_name, api_token, api_url)
    elif selection == '2':
        # Deploy a specific integration
        integration_name = input("Enter the name of the integration you want to deploy: ")
        extract_integration(integration_name)
        push_integration(api_url, integration_name, api_token)
        add_discoverable_to_integration("datadotworld-apps", integration_name, api_token, api_url)


def run():
    api_url = select_api_url("public")
    api_token = input("Enter your API Token for the site you are deploying integrations to: ")

    # Display integration list
    for integration in INTEGRATIONS:
        print(integration)

    selection = input("Enter '1' to deploy the default list of integrations, or '2' to specify an integration outside the list: ")

    if selection == '1' or selection == '2':
        deploy_integrations(api_url, api_token, selection)
    else:
        print("Invalid selection. Please enter '1' to deploy all listed integrations or '2' to deploy a specific integration.")

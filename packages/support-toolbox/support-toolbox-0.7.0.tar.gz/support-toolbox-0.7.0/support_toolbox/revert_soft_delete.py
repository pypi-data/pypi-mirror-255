import json
import requests
from support_toolbox.utils.helper import select_resource, select_api_url
import csv


# Revert soft delete for a resource
def revert_soft_delete(admin_token, org, iri, resource_type, customer_url):
    url = f"{customer_url}/editActivities/{org}/ddw-catalogs"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    resource_data = {
        "changeMessage": "Revert deleted resources",
        "activities": [{
            "type": "RevertSoftDelete",
            "entityType": resource_type,
            "target": iri
        }, {
            "type": "RevertSoftDelete",
            "entityType": resource_type,
            "target": iri
        }]
    }

    body = json.dumps(resource_data)
    response = requests.post(url, body, cookies=cookies, headers=header)

    # Verify the revert
    if response.status_code == 200:
        print(f"Successfully reverted soft delete for: {iri}")
    else:
        print(response.text)


# Handle CSV input
def process_csv_file(file_path):
    iris = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            iris.extend(row)
    return iris


def run():
    api_url = select_api_url("private")
    admin_token = input("Enter your active admin token for the selected customer: ")
    org = input("Enter the org ID where the resource is located: ")

    # Allow the user to input multiple IRIs as a comma-separated list or specify a CSV file path
    iris_input = input("Enter the resource IRIs (comma-separated) or specify a CSV file path: ")

    if iris_input.endswith('.csv'):
        # User provided a CSV file path, read and process it
        try:
            iris = process_csv_file(iris_input)
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return
    else:
        # User provided a comma-separated list, split and process it
        iris = [iri.strip() for iri in iris_input.split(',')]

    resource_type = select_resource()

    for iri in iris:
        revert_soft_delete(admin_token, org, iri, resource_type, api_url)

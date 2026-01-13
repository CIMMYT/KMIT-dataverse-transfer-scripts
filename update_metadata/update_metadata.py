from pyDataverse.api import NativeApi
from collections import defaultdict
from typing import Dict, Any

import argparse, csv

"""

Script to update dataset metadata
"""

# You need to input an valid API key to download restricted datafiles
api_token = 'YOUR_API_KEY_HERE'
base_url = 'https://demo.dataverse.org'

def argument_parser():
    parser = argparse.ArgumentParser(description="File to update metadata from Dataverse resources")
    parser.add_argument(
        "-f",
        "--file_metadata",
        type=str,
        required=True,
        help="The .csv file path with the fields and PID to update.",
    )

    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        default="update_metadata_responses.csv",
        required=False,
        help="The output .csv file path to save the responses. For default is 'update_metadata_responses.csv'.",
    )

    return parser

def csv_to_dict(file_path):
    """Convert a CSV file to a list of dictionaries."""
    data = []
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data



def dict_to_fields(metadata: Dict[str, Any]) -> Dict[str, Any]:
    fields = []
    compound_fields = defaultdict(list)

    for key, value in metadata.items():
        key = key.strip()  # limpia espacios accidentales

        if "." in key:
            parent, child = key.split(".", 1)

            compound_fields[parent].append(
                {
                    child: {
                        "typeName": child,
                        "value": value
                    }
                }
            )
        else:
            fields.append(
                {
                    "typeName": key,
                    "value": value
                }
            )

    # agregar los campos compuestos
    for parent, values in compound_fields.items():
        fields.append(
            {
                "typeName": parent,
                "value": values
            }
        )

    return {"fields": fields}


def format_pid(pid: str) -> str:
    """Format the PID to ensure it starts with 'doi:'."""
    if pid.startswith("https://doi.org"):
        return f"doi:{pid.replace('https://doi.org/', '')}", pid
    if pid.startswith("https://hdl.handle.net"):
        return f"hdl:{pid.replace('https://hdl.handle.net/', '')}", pid
    return pid, pid


if __name__ == "__main__":
    parser = argument_parser()
    args = parser.parse_args()

    api = NativeApi(base_url,api_token)

    input_file = args.file_metadata
    output_file = args.output_file

    metadata_list = csv_to_dict(input_file)

    responses = []
    for metadata in metadata_list:
        keys = list(metadata.keys())
        print(f"Updating metadata for PID: {metadata['pid']} - Metadata {metadata} - Keys: {keys}")
        pid, c_pid = format_pid(metadata.pop('pid'))
        fields_payload = dict_to_fields(metadata)
        response = api.get_dataset(pid,version=':latest', is_pid=True, auth=True)
        dataset_data = response.json().get('data',{}).get('latestVersion',{})
        dataset_version = dataset_data.get('versionState')
        # Update metadata
        update_response = api.edit_dataset_metadata(pid, fields_payload, is_pid= True, replace=True, auth=True)
        #update_response = None
        if dataset_version != 'DRAFT' and dataset_version == 'RELEASED':
            print(f"Dataset version is '{dataset_version}'. The script will create a new draft version and publish it after updating the metadata.")
            if update_response.status_code == 200:
                print("Metadata updated successfully on draft version."
                      "Proceeding to publish the dataset.")
                publish_response = api.publish_dataset(pid, release_type='minor', auth=True)
                if publish_response.status_code == 200:
                    print("Dataset published successfully.")
                    responses.append({"Identifier": c_pid,"pid": pid, "status": "published"})
                else:
                    print(f"Failed to publish dataset. Status code: {publish_response.status_code}")
            else:
                print(f"Failed to create draft version. Status code: {update_response.status_code}")
                continue  # Skip to the next metadata entry
        else:
            if update_response.status_code == 200:
                print("Metadata updated successfully on draft version.")
                responses.append({"Identifier": c_pid, "pid": pid, "status": "metadata updated but not published - DRAFT version"})
            else:
                print(f"Failed to update metadata. Status code: {update_response.status_code}")
                continue  # Skip to the next metadata entry

    # Save responses to a CVS file
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Identifier", "pid", "status"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for resp in responses:
            writer.writerow(resp)
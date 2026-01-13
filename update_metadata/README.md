# Dataverse Metadata Update Script

## Overview

This Python script **updates dataset metadata in Dataverse** using information provided in a CSV file.
It connects to a Dataverse instance through its API, updates the metadata of each dataset, and publishes the dataset if needed.

The script is useful when you need to update metadata in bulk instead of editing datasets one by one in the Dataverse web interface.

What the Script Does

* Reads a CSV file containing:
    - A dataset identifier (pid)
    - Metadata fields and values to update
* Converts the CSV data into the format required by the Dataverse API
* Updates the dataset metadata:
    - If the dataset is released, it creates a new draft, updates the metadata, and publishes it
    - If the dataset is already a draft, it only updates the metadata

* Saves the result of each update in an output CSV file

# Requirements

* Python 3.8 or higher
* A valid Dataverse API Token
* Access to a Dataverse instance
* Python libraries:
    - `pyDataverse`

You can install the require library with:

`pip install pyDataverse` or `pip install -r requirements.txt`


# Configuration

Before running the script, edit the following variables in the file:

- `api_token = 'YOUR_API_KEY_HERE'`
- `base_url = 'https://demo.dataverse.org'`

**api_token:** Your personal Dataverse API token

**base_url:** The URL of your Dataverse instance

# Input CSV Format

The CSV file must contain:

- A column named pid with the dataset identifier (DOI or Handle URL)
- One or more metadata fields as additional columns

Example:

> pid, title, dsDescription.dsDescriptionValue
> 
> https://doi.org/10.12345/ABC123 ,Sample Dataset ,This is a dataset description

Notes

- Simple fields (e.g. title) are handled automatically
- Compound fields use dot notation (e.g. dsDescription.dsDescriptionValue)


# How to Run the Script

`python update_metadata.py -f input_metadata.csv -o output_responses.csv`

## Arguments

- `-f` or `--file_metadata` - 
Path to the input CSV file (required)

- `-o` or `--output_file` -
Path to the output CSV file (optional)

Default: update_metadata_responses.csv


# Output

The script generates a CSV file with:

- Dataset identifier
- PID used in Dataverse
- Status of the operation (updated, published, or error)

Example output:

> Identifier,pid,status
>
> https://doi.org/10.12345/ABC123,doi:10.12345/ABC123,published


# Troubleshooting
## 1. `401 Unauthorized` or Authentication Errors

### Cause:

The API token is missing, incorrect, or does not have enough permissions.

### Solution:

- Make sure you replaced `YOUR_API_KEY_HERE` with a valid Dataverse API token
- Verify that the token belongs to a user with permission to edit the dataset
- Check that the `base_url` matches your Dataverse instance

## 2. Dataset Not Found (`404` Error)

### Cause:
The `pid` in the CSV file is incorrect or does not exist in the Dataverse instance.

### Solution:

- Verify the dataset exists and is accessible to your user
- Make sure the `pid` column contains a valid DOI or Handle URL
- Do not include extra spaces in the `pid` value

## 3. Metadata Field Is Ignored or Not Updated

### Cause:
The metadata field name does not match the Dataverse metadata schema.

### Solution:

- Ensure the column names in the CSV exactly match the Dataverse metadata field names
- For compound fields, use dot notation (example: `dsDescription.dsDescriptionValue`)
- Check that the metadata block is enabled in your Dataverse installation

## 4. Script Updates Metadata but Does Not Publish

### Cause:
The dataset is already in **DRAFT** state.

### Explanation:

The script only publishes datasets that were previously **RELEASED**.
Draft datasets are updated but remain unpublished.

### Solution:

- This behavior is expected
- If needed, publish the dataset manually from the Dataverse web interface

## 5. `KeyError: 'pid'`

### Cause:

The input CSV file does not contain a column named `pid`.

### Solution:
- Ensure the first row of the CSV includes a column named exactly pid
- Column names are case-sensitive

## 6. Encoding Errors When Reading the CSV File

### Cause:

The CSV file contains special characters and is not encoded in UTF-8.

### Solution:

- Save the CSV file using UTF-8 encoding
- If using Excel, choose **“UTF-8 (Comma delimited)”** when exporting

## 7. Nothing Happens or No Changes Appear in Dataverse

### Cause:
The dataset metadata was updated but cached or not refreshed in the UI.

### Solution:

- Refresh the dataset page in your browser
- Check the dataset version history to confirm the update
- Review the output CSV file for the operation status


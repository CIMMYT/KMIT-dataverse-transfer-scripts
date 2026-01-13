# KMIT Dataverse Transfer Scripts

  
Script to download files from a datafile in Dataverse. Use the official **Data Access API**.


## Dataverse File Downloader

A script for downloading all files from a Dataverse dataset using its unique identifier (either DOI or HANDLE).  
It leverages the official **Data Access API**.

## Requirements

- Python 3.8+

Install dependencies:

```bash
No dependencies required
````

## 
##  Usage

Before running the script, replace the values `api_token` and `dataset_id` with your API token and the PID (Persistent Identifier) of the dataset you want to download.

You may also need to modify the `dataset_version` value if you wish to specify a particular version of the dataset. By default, it will download the data from the latest published version.

`:latest-published`

If the dataset is not published or you want a draft version, use the option:

`:draft`

**Note:** To download draft versions, the user must have the necessary permissions.

More information: [Download By Dataset By Version](https://guides.dataverse.org/en/5.6/api/dataaccess.html#id7)

Then run the script:
```
python download_files.py
```

The script will:

-   Retrieve the dataset metadata using the provided PID (DOI or HANDLE).
    
-   Download **all associated files** into the current directory.


## References
- [Data Access API - Dataverse Docs](https://guides.dataverse.org/en/5.6/api/dataaccess.html)

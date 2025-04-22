from pyDataverse.api import NativeApi
import  os, requests, hashlib

# You need to input an valid API key to download restricted datafiles
api_token = 'PUT_YOUR_TOKEN_HERE'
# Replace this setting with the dataset's persistent ID (DOI or Handle)
dataset_id = 'DOI_OR_HANDLE'
# Replace this setting with the dataset's version number
# By default, the script will download data files from the latest published dataset version (:latest-published). If you want to download files from a draft version, use the :draft option.
# More information: https://guides.dataverse.org/en/5.6/api/dataaccess.html#download-by-dataset-by-version
#dataset_version = ':draft'
#dataset_version = '2.0'
dataset_version = ':latest-published'


# -------------------------------------------------------------------------#
#                       Do not edit this block                             #
# -------------------------------------------------------------------------#


base_url = 'https://data.cimmyt.org/'

def create_save_path(dataset_id):
    save_path = os.path.join(os.getcwd(), "dataset_"+dataset_id)
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
    return save_path

def get_dataset_version(dataset_id, version=':latest-published'):
    headers = {
        'X-Dataverse-key': api_token
    }
    if version == ':latest-published':
        url = f"{base_url}api/datasets/:persistentId/versions/:latest-published?persistentId={dataset_id}"
    else:
        url = f"{base_url}api/datasets/:persistentId/versions/{version}?persistentId={dataset_id}"
    # Realizar la solicitud GET para obtener la versión del conjunto de datos
    response = requests.get(url, headers=headers)
    # Verificar si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def download_file(url, save_path):
    headers = {
        'X-Dataverse-key': api_token
    }
    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url, headers=headers, stream=True)
    
    # Verificar si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        # Guardar el archivo en el directorio especificado
        print(f"Downloading file: {url}")
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=4096):
                file.write(chunk)
        print(f"File downloaded: {save_path} \n ---------------- \n")
    else:
        print(f"Error downloading file: {response.status_code}")

def write_md5_checksum(checksum_file, checksum_entry):	
    # Ensure no duplicate entries
    if os.path.exists(checksum_file):
        with open(checksum_file, "r") as f:
            existing_entries = f.read().splitlines()
        if checksum_entry in existing_entries:
            print("Checksum entry already exists, skipping.")
            return
    with open(checksum_file, "a") as f:
        f.write(checksum_entry + "\n")

def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def file_exists(file_path, checksum):
    if os.path.exists(file_path) and checksum == calculate_md5(file_path):
        print("File exists and checksum matches")
        return True
    return False

def main():
    api = NativeApi(base_url,api_token)
    dataset = get_dataset_version(dataset_id,version = dataset_version)
    save_path=create_save_path(dataset_id.split("/")[1])
    files_list = dataset['data']['files']
    for file in files_list:
        filename = file["dataFile"]["filename"]
        file_id = file["dataFile"]["id"]
        file_checksum = file["dataFile"]["checksum"]["value"]
        print("----------------\n")
        print("File name {}, id {}, cheksum {}".format(filename, file_id, file_checksum))
        file_url = base_url + "api/access/datafile/" + str(file_id)
        if not file_exists(save_path+"/"+filename, file_checksum):
            print("File does not exist, downloading")
            download_file(file_url, save_path+"/"+filename)
        write_md5_checksum(save_path+"/CHECKSUMS", file_checksum + "\t" + filename)
        print("----------------\n")

if __name__ == "__main__":
    main()

# -------------------------------------------------------------------------#
#                       Do not edit this block                             #
# -------------------------------------------------------------------------#
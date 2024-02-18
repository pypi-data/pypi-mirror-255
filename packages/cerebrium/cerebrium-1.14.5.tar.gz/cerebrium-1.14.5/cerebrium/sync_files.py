import datetime
import hashlib
import io
import json
import os
import requests
from typing import List, Dict
from typing import TypedDict
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from cerebrium import datatypes, utils

debug = os.environ.get("LOG_LEVEL", "INFO") == "DEBUG"


class FileData(TypedDict):
    fileName: str
    hash: str


class UploadURLsResponse(TypedDict):
    uploadUrls: Dict[str, str]
    deleteKeys: List[str]
    markerFile: str


def get_md5(file_path: str) -> str:
    """Return MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


def gather_hashes(file_list: List[str], base_dir: str = "") -> List[Dict[str, str]]:
    """Gather the MD5 hashes of the local files including subdirectories."""
    local_files_payload: List[Dict[str, str]] = []

    for file in file_list:
        if file.startswith("./"):
            file = file[2:]
        if base_dir and file.startswith(base_dir):
            file_name = os.path.relpath(file, base_dir)
        else:
            file_name = file
        if os.path.isfile(file):
            file_hash = get_md5(file)
            local_files_payload.append({"fileName": file_name, "hash": file_hash})

    return local_files_payload


def upload_files_to_s3(upload_urls: Dict[str, str], base_dir: str = "") -> int:
    print(f"Uploading {len(upload_urls)} files...")

    file_keys = list(upload_urls.keys())
    working_dir = base_dir or os.getcwd()

    # Calculate total size of all files
    total_size = sum(
        os.path.getsize(os.path.join(working_dir, file_data))
        for file_data in file_keys
        if os.path.isfile(os.path.join(working_dir, file_data))
    )

    uploaded_count = 0
    with tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="Upload Progress",
    ) as pbar:
        for file_data in file_keys:
            if file_data in upload_urls:
                file_name = file_data
                file_path = os.path.join(working_dir, file_name)
                # print("DEBUG: Uploading file", file_path, "to S3 under", file_name)
                with open(file_path, "rb") as file:
                    if os.stat(file_path).st_size == 0:
                        upload_response = requests.put(upload_urls[file_name], data=b"")
                    else:
                        wrapped_file = CallbackIOWrapper(pbar.update, file, "read")
                        upload_response = requests.put(
                            upload_urls[file_name],
                            data=wrapped_file,
                            timeout=60,
                            stream=True,
                        )
                    if upload_response.status_code != 200:
                        raise Exception(
                            f"Failed to upload {file_name}. Status code: {upload_response.status_code}"
                        )
                    uploaded_count += 1

    return uploaded_count


def upload_marker_file_and_delete(url: str, uploaded_count: int, build_id: str) -> None:
    """Upload the marker file with JSON content without actually writing anything to disk."""

    # Construct the marker file content
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    marker_content = {
        "Date": current_date,
        "Files Uploaded": uploaded_count,
        "buildId": build_id,
    }

    # Convert the dictionary to a JSON formatted string
    json_content = json.dumps(marker_content)

    # Simulate the marker file in memory
    marker_file_content = json_content.encode()  # Convert to bytes
    marker_file = io.BytesIO(marker_file_content)

    upload_response = requests.put(url, data=marker_file)
    if upload_response.status_code != 200:
        marker_file_name = "upload.complete"

        raise Exception(
            f"Failed to upload {marker_file_name}. Status code: {upload_response.status_code}"
        )
    print("Uploaded complete.")


def make_cortex_util_files(temp_dir: str, config: datatypes.CerebriumConfig):

    # Remove requirements.txt, pkglist.txt, conda_pkglist.txt from file_list if they exist. Will be added from config
    files_to_remove = [
        "requirements.txt",
        "conda_pkglist.txt",
        "pkglist.txt",
        "./requirements.txt",
        "./conda_pkglist.txt",
        "./pkglist.txt",
    ]
    config.file_list = [f for f in config.file_list if f not in files_to_remove]

    # write a predict config file containing the prediction parameters
    predict_file = os.path.join(
        temp_dir, "_cerebrium_predict.json"
    )  # use a file to avoid storing large files in the model objects in ddb
    if config.build.predict_data is not None:
        with open(predict_file, "w") as f:
            f.write(
                config.build.predict_data
            )  # predict data has been validated as a json string previously

    # Create files temporarily for upload
    requirements_files = [
        ("requirements.txt", config.dependencies.pip),
        ("pkglist.txt", config.dependencies.apt),
        ("conda_pkglist.txt", config.dependencies.conda),
    ]

    for file_name, reqs in requirements_files:
        if reqs:
            utils.requirements_to_file(reqs, os.path.join(temp_dir, file_name))

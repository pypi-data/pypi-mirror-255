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


def gather_hashes(file_list: List[str]) -> List[Dict[str, str]]:
    """Gather the MD5 hashes of the local files including subdirectories."""
    local_files_payload = []

    for file in file_list:
        if file.startswith("./"):
            file = file[2:]
        if os.path.isfile(file):
            file_hash = get_md5(file)
            local_files_payload.append({"fileName": file, "hash": file_hash})

    return local_files_payload


def upload_files_to_s3(upload_urls) -> None:
    print(f"Uploading {len(upload_urls)} files...")

    file_keys = list(upload_urls.keys())

    # Calculate total size of all files
    total_size = sum(
        os.path.getsize(os.path.join(os.getcwd(), file_data))
        for file_data in file_keys
        if os.path.isfile(os.path.join(os.getcwd(), file_data))
    )

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
                file_path = os.path.join(os.getcwd(), file_name)

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

    marker_file_name = "upload.complete"

    # Simulate the marker file in memory
    marker_file_content = json_content.encode()  # Convert to bytes
    marker_file = io.BytesIO(marker_file_content)

    upload_response = requests.put(url, data=marker_file)
    if upload_response.status_code != 200:
        raise Exception(
            f"Failed to upload {marker_file_name}. Status code: {upload_response.status_code}"
        )
    print(f"Uploaded complete.")

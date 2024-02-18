import re
import math
import time
import requests
import os
import logging
from ..common.api_request import make_request
from tqdm.utils import CallbackIOWrapper

# 128MB
MAX_CHUNK_SIZE = 2 ** 27

def perform_resumable_upload(data, table_uri, progressbar=None):
    start_byte = 0
    retry_count = 0
    did_reopen_file = False
    is_file = True if hasattr(data, "read") else False
    file_size = os.stat(data.name).st_size if is_file else len(data)
    chunk_size = file_size


    if is_file and hasattr(data, 'mode') and 'b' not in data.mode:
        data = open(data.name, 'rb')
        did_reopen_file = True

    res = make_request(
        path=f"{table_uri}/resumableUpload",
        method="POST",
        payload={"size": file_size},
    )
    resumable_uri = res["url"]
    resumable_upload_id = res["id"]

    while start_byte < file_size:
        end_byte = min(start_byte + chunk_size - 1, file_size - 1)
        if is_file:
            data.seek(start_byte)
            if progressbar:
                chunk = CallbackIOWrapper(progressbar.update, data, "read")
            else:
                chunk = data
        else:
            if start_byte != 0:
                chunk = data[start_byte : end_byte + 1]
            else:
                chunk = data

        try:
            res = requests.put(
                url=resumable_uri,
                headers={
                    "Content-Length": f"{end_byte - start_byte + 1}",
                    "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                },
                data=chunk,
            )
            res.raise_for_status()

            start_byte += chunk_size
            retry_count = 0
        except Exception as e:
            print(e)
            if retry_count > 20:
                print("A network error occurred. Upload failed after too many retries.")
                raise e

            retry_count += 1
            time.sleep(retry_count)
            print("A network error occurred. Retrying last chunk of resumable upload.")
            start_byte = retry_partial_upload(
                file_size=file_size, resumable_uri=resumable_uri
            )

    if did_reopen_file:
        data.close()

    return resumable_upload_id

def retry_partial_upload(*, retry_count=0, file_size, resumable_uri):
    logging.debug("Attempting to resume upload")

    try:
        res = requests.put(
            url=resumable_uri,
            headers={"Content-Length": "0", "Content-Range": f"bytes */{file_size}"},
        )

        if res.status_code == 404:
            return 0

        res.raise_for_status()

        if res.status_code == 200 or res.status_code == 201:
            return file_size
        elif res.status_code == 308:
            range_header = "Range" in res.headers

            if range_header:
                match = re.match(r"bytes=0-(\d+)", range_header)
                if match.group(0) and not math.isnan(int(match.group(1))):
                    return int(match.group(1)) + 1
                else:
                    raise Exception("An unknown error occurred. Please try again.")
            # If GCS hasn't received any bytes, the header will be missing
            else:
                return 0
    except Exception as e:
        if retry_count > 10:
            raise e

        time.sleep(retry_count / 10)
        retry_partial_upload(
            retry_count=retry_count + 1,
            file_size=file_size,
            resumable_uri=resumable_uri,
        )
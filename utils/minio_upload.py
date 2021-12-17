import os
from datetime import datetime
import uuid
import sys
import requests
from minio import Minio, error
import warnings

with open("config.json", "r") as f:
    config = eval(f.read()

is_https = config["is_https"]
server_url = config["server_url"]
secret_key = config["secret_key"]
access_key = config["access_key"]
bucket_name = config["bucket_name"]
object_path = config["object_path"]

# warnings.filterwarnings('ignore')
minioClient = Minio(server_url,
                    access_key=access_key,
                    secret_key=secret_key,
                    secure=is_https) # https if True

def expand_object_path():
    # expand time format string
    new_path = datetime.now().strftime(object_path)
    return new_path

def download_temp(image_url):
    local_path = os.getcwd() + "/temp"
    r = requests.get(image_url, verify=False)
    with open(local_path, "wb") as code:
        code.write(r.content)
    return local_path

# image path, support http or local
# return is_error, new_url 
def upload_fobject(image):
    new_file_name = os.path.basename(image)
    # process web images
    if image.startswith("https://") or image.startswith("http://"):
        image = download_temp(image)
    else:
        image = os.path.realpath(os.path.expandvars(image))

    if not os.path.isfile(image):
        return "error: parsing image error!"

    try:
        object_name = os.path.join(expand_object_path(), new_file_name)
        minioClient.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=image)
        if image.endswith("temp"):
            os.remove(image)
    except error.MinioException as err:
        return "error: " + err.message
    return os.path.join(
            ("https://" if is_https else "http://") + server_url,
            bucket_name, object_name)


if __name__ == "__main__":
    images = sys.argv[1:]
    for image in images:
        result = upload_fobject(image)
        print(result)


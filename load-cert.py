import requests
import shutil
import json
import logging
import tempfile
import zipfile
import os
import argparse

logger = logging.getLogger(__name__)
charset = "UTF-8"


def get_token(host_adress, user_email, user_password):
    token = None
    url = f"http://{host_adress}/api/tokens"
    headers = {
        "Content-Type": f"application/json; charset={charset}",
    }
    json_data = {
        "identity": user_email,
        "secret": user_password,
    }
    res = requests.post(url, headers=headers, json=json_data)
    if res.status_code == 200:
        token = json.loads(res.content.decode(charset))["token"]
        logger.info("Token successfully received")
    else:
        message = res.content.decode(charset)
        logger.error(f"Failed to get access key.  Message: message{message}")

    return token


def get_info(host_adress, token, path, params=None):
    responce_data = None
    headers = {
        "Content-Type": f"application/json; charset={charset}",
        "Authorization": f"Bearer {token}",
    }
    url = f"http://{host_adress}{path}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        responce_data = json.loads(res.content.decode(charset))
        logger.info(f"The request was completed successfully. {responce_data}")
    else:
        message = res.content.decode(charset)
        logger.error(f"Failed to get access key.  Message: message{message}")
    return responce_data


def get_cert_archive(host_adress, token, path):
    headers = {
        "Content-Type": f"application/json; charset={charset}",
        "Authorization": f"Bearer {token}",
    }
    url = f"http://{host_adress}{path}"
    res = requests.get(url, headers=headers, stream=True)
    if res.status_code == 200:
        arch_path = tempfile.NamedTemporaryFile(suffix=".zip").name
        res.raw.decode_content = True
        with open(arch_path, "wb") as f:
            shutil.copyfileobj(res.raw, f)
            logger.info("The certs archive was downloaded: {arch_path}")
            return arch_path
    else:
        message = res.content.decode(charset)
        logger.error(f"Failed to download certs archive.  Message: message{message}")
    return None


def get_cert_id(certs_info, cert_domain_name):
    for cert_info in certs_info:
        for domain_name in cert_info["domain_names"]:
            if domain_name == cert_domain_name:
                id = cert_info["id"]
                logger.info(f"The cert id={id}")
                return id
    logger.error("The cert id not found")
    return None


def extract_cert(archive_path, key_path, cert_path):
    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        for file_info in zip_ref.filelist:
            if "fullchain" in file_info.filename:
                with open(cert_path, "wb") as f:
                    f.write(zip_ref.read(file_info))
                    logger.info(f"extract {cert_path}")
            if "privkey" in file_info.filename:
                with open(key_path, "wb") as f:
                    f.write(zip_ref.read(file_info))
                    logger.info(f"extract {key_path}")
    zip_ref.close()
    os.remove(archive_path)
    logger.info(f"remove {archive_path}")


def load_certs(
    host_adress, user_email, user_password, cert_domain_name, key_path, cert_path
):
    token = get_token(host_adress, user_email, user_password)
    if token == None:
        exit(1)

    # Список сертификатов
    path = "/api/nginx/certificates"
    params = {"expand": "owner"}
    resp_json = get_info(host_adress, token, path=path, params=params)
    if resp_json == None:
        exit(1)

    # Ищем ID сертификата
    cert_id = get_cert_id(resp_json, cert_domain_name)
    if cert_id == None:
        exit(1)

    # Качаем архив
    archive_path = get_cert_archive(
        host_adress, token, f"/api/nginx/certificates/{cert_id}/download"
    )
    if archive_path == None:
        exit(1)

    extract_cert(archive_path, key_path, cert_path)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )

    parser = argparse.ArgumentParser(
        description="Nginx Proxy Manager Certificate Downloader"
    )
    parser.add_argument(
        "-hp", "--host_port", help="Nginx host url and port. Format: 127.0.0.1:81"
    )
    parser.add_argument("-u", "--user", help="Nginx user email")
    parser.add_argument("-p", "--password", help="Nginx user password")
    parser.add_argument("-d", "--domain", help="Cert domain name")
    parser.add_argument("-k", "--key", help="Target filename for key file")
    parser.add_argument("-c", "--cert", help="Target filename for certtificate file")
    args = parser.parse_args()

    args_valid = True
    arg_values = vars(args)
    for key in arg_values:
        if arg_values[key] == None:
            args_valid = False
            logger.error(f'argument --{key} is not set')
            
    if not args_valid:            
        exit(1)
        
    load_certs(
        host_adress=args.host_port,
        user_email=args.user,
        user_password=args.password,
        cert_domain_name=args.domain,
        key_path=args.key,
        cert_path=args.cert,
    )

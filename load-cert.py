import argparse
import logging
import os
import shutil
import tempfile
import zipfile

import requests

logger = logging.getLogger(__name__)
CHARSET = "UTF-8"


def build_url(host_address, path):
    if host_address.startswith(("http://", "https://")):
        return f"{host_address.rstrip('/')}{path}"
    return f"http://{host_address.rstrip('/')} {path}".replace(" ", "")


def get_token(host_address, user_email, user_password):
    url = build_url(host_address, "/api/tokens")
    headers = {"Content-Type": f"application/json; charset={CHARSET}"}
    payload = {"identity": user_email, "secret": user_password}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        logger.error(f"Failed to get token: {exc}")
        return None

    if response.status_code == 200:
        try:
            token = response.json()["token"]
            logger.info("Token successfully received")
            return token
        except (ValueError, KeyError) as exc:
            logger.error(f"Invalid token response: {exc}")
            return None

    logger.error(f"Failed to get access key. Message: {response.text}")
    return None


def get_info(host_address, token, path, params=None):
    url = build_url(host_address, path)
    headers = {
        "Content-Type": f"application/json; charset={CHARSET}",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
    except requests.RequestException as exc:
        logger.error(f"Request failed: {exc}")
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            logger.info(f"The request was completed successfully. {data}")
            return data
        except ValueError as exc:
            logger.error(f"Invalid JSON response: {exc}")
            return None

    logger.error(f"Failed to get access key. Message: {response.text}")
    return None


def get_cert_archive(host_address, token, path):
    url = build_url(host_address, path)
    headers = {
        "Content-Type": f"application/json; charset={CHARSET}",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
    except requests.RequestException as exc:
        logger.error(f"Failed to download certs archive: {exc}")
        return None

    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            archive_path = temp_file.name

        try:
            response.raw.decode_content = True
            with open(archive_path, "wb") as archive_file:
                shutil.copyfileobj(response.raw, archive_file)
            logger.info(f"The certs archive was downloaded: {archive_path}")
            return archive_path
        except OSError as exc:
            logger.error(f"Could not save archive: {exc}")
            if os.path.exists(archive_path):
                os.remove(archive_path)
            return None

    logger.error(f"Failed to download certs archive. Message: {response.text}")
    return None


def get_cert_id(certs_info, cert_domain_name):
    for cert_info in certs_info or []:
        for domain_name in cert_info.get("domain_names", []):
            if domain_name == cert_domain_name:
                cert_id = cert_info["id"]
                logger.info(f"The cert id={cert_id}")
                return cert_id
    logger.error("The cert id not found")
    return None


def extract_cert(archive_path, key_path, cert_path):
    key_dir = os.path.dirname(key_path) or "."
    cert_dir = os.path.dirname(cert_path) or "."
    os.makedirs(key_dir, exist_ok=True)
    os.makedirs(cert_dir, exist_ok=True)

    found_key = False
    found_cert = False

    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            filename_lower = file_info.filename.lower()
            if "fullchain" in filename_lower:
                with open(cert_path, "wb") as cert_file:
                    cert_file.write(zip_ref.read(file_info))
                logger.info(f"extract {cert_path}")
                found_cert = True
            if "privkey" in filename_lower:
                with open(key_path, "wb") as key_file:
                    key_file.write(zip_ref.read(file_info))
                logger.info(f"extract {key_path}")
                found_key = True

    if not found_key or not found_cert:
        raise ValueError("Certificate archive does not contain key or fullchain files")

    os.remove(archive_path)
    logger.info(f"remove {archive_path}")


def load_certs(
    host_address, user_email, user_password, cert_domain_name, key_path, cert_path
):
    token = get_token(host_address, user_email, user_password)
    if token is None:
        raise SystemExit(1)

    path = "/api/nginx/certificates"
    params = {"expand": "owner"}
    resp_json = get_info(host_address, token, path=path, params=params)
    if resp_json is None:
        raise SystemExit(1)

    cert_id = get_cert_id(resp_json, cert_domain_name)
    if cert_id is None:
        raise SystemExit(1)

    archive_path = get_cert_archive(
        host_address, token, f"/api/nginx/certificates/{cert_id}/download"
    )
    if archive_path is None:
        raise SystemExit(1)

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
        "-hp",
        "--host_port",
        required=True,
        help="Nginx host url and port. Format: 127.0.0.1:81",
    )
    parser.add_argument("-u", "--user", required=True, help="Nginx user email")
    parser.add_argument("-p", "--password", required=True, help="Nginx user password")
    parser.add_argument("-d", "--domain", required=True, help="Cert domain name")
    parser.add_argument(
        "-k", "--key", required=True, help="Target filename for key file"
    )
    parser.add_argument(
        "-c", "--cert", required=True, help="Target filename for certificate file"
    )
    args = parser.parse_args()

    load_certs(
        host_address=args.host_port,
        user_email=args.user,
        user_password=args.password,
        cert_domain_name=args.domain,
        key_path=args.key,
        cert_path=args.cert,
    )

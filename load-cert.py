import requests
import json
import logging

logger = logging.getLogger(__name__)
charset = 'UTF-8'


def get_token(host_adress, user_email, user_password):
    token = None
    url = f'http://{host_adress}/api/tokens'
    headers = {
        'Content-Type': f'application/json; charset={charset}',
    }
    json_data = {
        'identity': user_email,
        'secret': user_password,
    }
    res = requests.post(url, headers=headers, json=json_data)
    if res.status_code == 200:
        token = json.loads(res.content.decode(charset))['token']
        logger.info('Token successfully received')
    else:
        message = res.content.decode(charset)
        logger.error(
            f'Failed to get access key.  Message: message{message}')

    return token


def get_info(host_adress, token, path, params=None):
    responce_data = None
    headers = {
        'Content-Type': f'application/json; charset={charset}',
        'Authorization': f'Bearer {token}',
    }
    url = f'http://{host_adress}{path}'
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        responce_data = json.loads(res.content.decode(charset))
        logger.info(f'The request was completed successfully. {responce_data}')
    else:
        message = res.content.decode(charset)
        logger.error(
            f'Failed to get access key.  Message: message{message}')
    return responce_data

def get_binary(host_adress, token, path):
    responce_data = None
    headers = {
        'Content-Type': f'application/json; charset={charset}',
        'Authorization': f'Bearer {token}',
    }
    url = f'http://{host_adress}{path}'
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        responce_data = res.content
        # logger.info(f'The request was completed successfully. {responce_data}')
    else:
        message = res.content.decode(charset)
        logger.error(
            f'Failed to get access key.  Message: message{message}')
    return responce_data

def load_certs(host_adress, user_email, user_password):
    token = get_token(host_adress, user_email, user_password)
    if token == None:
        exit(1)

    # Список проксируемых хостов
    path = '/api/nginx/proxy-hosts'
    params = {'expand': 'owner,access_list,certificate'}
    resp_json = get_info(host_adress, token, path=path, params=params)

    # Список сертификатов
    path = '/api/nginx/certificates'
    params = {'expand': 'owner'}
    resp_json = get_info(host_adress, token, path=path, params=params)
    pass

    # /api/nginx/certificates/{certID}/download

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    host_adress = 'localhost:81'
    user_email = 'bot@loader.key'
    user_password = 'Eevuwie0ier5Gim8'
    cert_domain_name = 'm.t.ru'
    load_certs(host_adress, user_email, user_password)

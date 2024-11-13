import requests
import json
import logging

logger = logging.getLogger(__name__)


def get_token(host_adress, user_email, user_password):
		token = None
		charset = 'UTF-8'
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
		else:
				message = res.content.decode(charset)
				logger.error(
						f'Failed to get access key.  Message: message{message}')

		return token


def load_certs(host_adress, user_email, user_password):
		token = get_token(host_adress, user_email, user_password)
		if token == None:
				exit(1)


if __name__ == '__main__':
		logging.basicConfig(
				format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
		)
		host_adress = 'localhost:81'
		user_email = 'bot@loader.key'
		user_password = 'Eevuwie0ier5Gim8'

		load_certs(host_adress, user_email, user_password)

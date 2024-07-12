from constants import PROXYAI_TOKEN
import requests
from pprint import pprint

url = "https://api.proxyapi.ru/proxyapi/balance"
headers = {
    "Authorization": f"Bearer {PROXYAI_TOKEN}"
}


response = requests.get(url, headers=headers)

if response.status_code == 402:
    print('Недостаточно средств для выполнения запроса.')
data = response.json()
pprint(data['balance'])
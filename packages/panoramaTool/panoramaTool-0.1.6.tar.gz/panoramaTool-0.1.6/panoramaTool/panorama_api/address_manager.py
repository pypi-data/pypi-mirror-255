import json

import requests


class AddressManager:
    def __init__(self, panorama_url, api_key, verify=True):
        self.panorama_url = panorama_url
        self.api_key = api_key
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Objects/Addresses"
        self.headers = {'Content-Type': 'application/json',
                        'X-PAN-KEY': f"{self.api_key}"}

    def list_addresses(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        addresses = json.loads(response.content.decode('utf-8'))
        return addresses

    def create_address(self, name, ip, cidr, description):
        params = {'name': name, 'location': 'shared', 'device-group': 'TestGroup'}
        payload = self._get_address_payload(name, ip, cidr, description)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        return json.loads(response.content.decode('utf-8'))

    def _get_address_payload(self, name, ip, cidr, description):
        address_payload = {
            'entry': [
                {
                    '@name': name,
                    '@location': 'TestGroup',
                    'ip-netmask': f'{ip}/{cidr}',
                    'description': description
                }
            ]
        }
        return address_payload

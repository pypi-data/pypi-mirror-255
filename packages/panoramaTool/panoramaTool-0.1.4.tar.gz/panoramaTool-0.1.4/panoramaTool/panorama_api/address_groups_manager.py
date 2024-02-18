import json

import requests


class AddressGroupsManager:
    def __init__(self, panorama_url, api_key, verify=True):
        self.panorama_url = panorama_url
        self.api_key = api_key
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Objects/AddressGroups"
        self.headers = {"Content-Type": "application/json",
                        'X-PAN-KEY': f"{self.api_key}"}

    def list_address_groups(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        address_groups = json.loads(response.content.decode('utf-8'))
        return address_groups

    def create_address_group(self, name: str, members: str, description: str):
        params = {'name': name, 'location': 'shared', 'device-group': 'TestGroup'}
        payload = self._get_address_group_payload(name=name, members=members, description=description)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        address_group = json.loads(response.content.decode('utf-8'))
        return address_group

    def _get_address_group_payload(self, name: str, members: str, description: str):
        address_group_payload = {
            'entry': [
                {
                    '@name': name,
                    '@location': 'shared',
                    'static':
                        {
                            'member': members.split('\n')
                        },
                    'description': description
                }
            ]
        }
        print(address_group_payload)
        return address_group_payload

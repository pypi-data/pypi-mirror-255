import json

import requests


class ServiceGroupsManager:
    def __init__(self, panorama_url, api_key, verify=True):
        self.panorama_url = panorama_url
        self.api_key = api_key
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Objects/ServiceGroups"
        self.headers = {"Content-Type": "application/json",
                        'X-PAN-KEY': f"{self.api_key}"}

    def list_service_groups(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        service_groups = json.loads(response.content.decode('utf-8'))
        return service_groups

    def create_service_group(self, device_group: str, name: str, members: str):
        location = "shared" if device_group == 'shared' else "device-group"
        params = {'name': name, 'location': location, 'device-group': device_group}
        payload = self._get_service_group_payload(device_group=device_group, name=name, members=members)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        service_group = json.loads(response.content.decode('utf-8'))
        return service_group

    def _get_service_group_payload(self, device_group: str, name: str, members: str):
        service_group_payload = {
            'entry': [
                {
                    '@name': name,
                    '@location': device_group,
                    'members':
                        {
                            'member': members.split('\n')
                        },
                }
            ]
        }
        print(service_group_payload)
        return service_group_payload

import json

import requests


class PostRulesManager:
    def __init__(self, panorama_url, api_key, verify=True):
        self.panorama_url = panorama_url
        self.api_key = api_key
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Policies/SecurityPostRules"
        self.headers = {'Content-Type': 'application/json',
                        'X-PAN-KEY': f"{self.api_key}"}

    def list_post_rules(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        post_rules = json.loads(response.content.decode('utf-8'))
        return post_rules

    def create_post_rules(self, device_group, name, action, description, from_zone, source_group,
                          to_zone, destination_group, service, profile_type, profile):
        location = "shared" if device_group == 'shared' else "device-group"
        params = {'name': name, 'location': location, 'device-group': device_group}
        payload = self._get_post_rules_payload(device_group, name, action, description, from_zone, source_group,
                                               to_zone, destination_group, service, profile_type, profile)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        return json.loads(response.content.decode('utf-8'))

    def _get_post_rules_payload(self, device_group, name, action, description, from_zone, source_group,
                          to_zone, destination_group, service, profile_type, profile):
        security_policy_payload = {
            "entry": [
                {
                    "@location": device_group,
                    "@name": name,
                    "description": description,
                    "@vsys": "vsys1",
                    "action": action,
                    "from": {
                        "member": [
                            from_zone.split('\n')
                        ]
                    },
                    "to": {
                        "member": [
                            to_zone.split('\n')
                        ]
                    },
                    "source": {
                        "member": [
                            source_group.split('\n')
                        ]
                    },
                    "destination": {
                        "member": [
                            destination_group.split('\n')
                        ]
                    },
                    "service": {
                        "member": [
                            service.split('\n')
                        ]
                    },
                    "application": {
                        "member": [
                            "any"
                        ]
                    },
                    "tag": {
                        "member": [
                            "to_be_reviewed"
                        ]
                    },
                    'profile-setting': {
                        profile_type: {
                            'member': [
                                profile
                            ]
                        }
                    }
                }
            ]
        }
        return security_policy_payload

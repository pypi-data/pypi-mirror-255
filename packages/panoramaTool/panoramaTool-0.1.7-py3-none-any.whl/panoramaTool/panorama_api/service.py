import json

import requests


class ServiceManager:
    def __init__(self, panorama_url, apikey, verify=True):
        self.panorama_url = panorama_url
        self.apikey = apikey
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Objects/Services"
        self.headers = {"Content-Type": "application/json",
                        'X-PAN-KEY': f"{self.apikey}"}

    def list_services(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        services = json.loads(response.content.decode('utf-8'))
        return services

    def create_service(self, protocol, port):
        params = {'name': f"{protocol}_{port}", 'location': 'shared', 'device-group': 'TestGroup'}
        payload = self._get_service_payload(protocol=protocol, port=port)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        service = json.loads(response.content.decode('utf-8'))
        return service

    def _get_service_payload(self, protocol, port):
        service_payload = {
            "entry": {
                "@name": f"{protocol}_{port}",
                "description": f"{protocol}_{port}",
                "protocol": {
                    protocol.lower(): {
                        "port": port
                    },
                },
            },
        }
        return service_payload

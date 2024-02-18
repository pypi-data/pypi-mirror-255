import json

import requests

from panoramaTool.panorama_api.service import ServiceManager


class PostRulesManager:
    def __init__(self, panorama_url, apikey, verify=True):
        self.panorama_url = panorama_url
        self.apikey = apikey
        self.verify = verify
        self.url = f"{self.panorama_url}/restapi/v10.2/Policies/SecurityPostRules"
        self.headers = {"Content-Type": "application/json",
                        'X-PAN-KEY': f"{self.apikey}"}
        self.service_manager = ServiceManager(panorama_url=panorama_url, apikey=apikey, verify=verify)

    def list_port_rules(self):
        params = {'location': 'shared', 'device-group': 'TestGroup'}
        response = requests.get(url=self.url, headers=self.headers, params=params, verify=self.verify)
        port_rules = json.loads(response.content.decode('utf-8'))
        return port_rules

    def create_post_rule(self, action, source_address, source_zone,
                         destination_address, destination_zone, protocol,
                         destination_port, name, application):
        params = {'name': name, 'location': 'shared', 'device-group': 'TestGroup'}

        if "icmp" not in protocol.lower():
            if f"{protocol}_{destination_port}" not in self.service_manager.list_services():
                self.service_manager.create_service(protocol=protocol, port=destination_port)

            payload = self._get_security_policy_payload_for_tcp_and_udp(action=action,
                                                                        source_address=source_address,
                                                                        source_zone=source_zone,
                                                                        destination_address=destination_address,
                                                                        destination_zone=destination_zone,
                                                                        protocol=protocol,
                                                                        destination_port=destination_port,
                                                                        name=name,
                                                                        application=application)
        else:
            payload = self._get_security_policy_payload_for_icmp(action=action,
                                                                 source_address=source_address,
                                                                 source_zone=source_zone,
                                                                 destination_address=destination_address,
                                                                 destination_zone=destination_zone,
                                                                 name=name)
        response = requests.post(url=self.url, headers=self.headers, params=params, data=json.dumps(payload),
                                 verify=self.verify)
        device_group = json.loads(response.content.decode('utf-8'))
        return device_group

    def _get_security_policy_payload_for_tcp_and_udp(self, action, source_address, source_zone,
                                                     destination_address, destination_zone, protocol,
                                                     destination_port, name, application):
        security_policy_payload = {
            "entry": [
                {
                    "@location": "vsys",
                    "@name": name,
                    "@vsys": "vsys1",
                    "action": action,
                    "from": {
                        "member": [
                            source_zone
                        ]
                    },
                    "to": {
                        "member": [
                            destination_zone
                        ]
                    },
                    "source": {
                        "member": [
                            source_address
                        ]
                    },
                    "destination": {
                        "member": [
                            destination_address
                        ]
                    },
                    "service": {
                        "member": [
                            f"{protocol}_{destination_port}"
                        ]
                    },
                    "application": {
                        "member": [
                            application
                        ]
                    },
                    "tag": {
                        "member": [
                            "to be reviewed"
                        ]
                    },
                }
            ]
        }
        return security_policy_payload

    def _get_security_policy_payload_for_icmp(self, action, source_address, source_zone,
                                              destination_address, destination_zone,
                                              name):
        security_policy_payload = {
            "entry": [
                {
                    "@location": "vsys",
                    "@name": name,
                    "@vsys": "vsys1",
                    "action": action,
                    "from": {
                        "member": [
                            source_zone
                        ]
                    },
                    "to": {
                        "member": [
                            destination_zone
                        ]
                    },
                    "source": {
                        "member": [
                            source_address
                        ]
                    },
                    "destination": {
                        "member": [
                            destination_address
                        ]
                    },
                    "service": {
                        "member": [
                            "application-default"
                        ]
                    },
                    "application": {
                        "member": [
                            "ping"
                        ]
                    },
                    "tag": {
                        "member": [
                            "to be reviewed"
                        ]
                    },
                }
            ]
        }
        return security_policy_payload

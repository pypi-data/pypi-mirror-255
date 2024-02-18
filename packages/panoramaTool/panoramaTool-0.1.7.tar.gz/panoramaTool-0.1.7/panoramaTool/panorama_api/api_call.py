import os
from xml.etree import ElementTree

import requests


class APICall:

    @staticmethod
    def get_api_key(panorama_url, user, password) -> str:
        user = user
        password = password
        key_response = requests.get(url=f"{panorama_url}/api/?type=keygen&user={user}&password={password}",
                                    verify=False)
        xml_key = key_response.content.decode('utf-8')
        root = ElementTree.fromstring(xml_key)
        try:
            api_key = root.find(".//key").text
            return api_key
        except AttributeError:
            return "Invalid Credentials"

    @staticmethod
    def check_valid_key(panorama_url, api_key) -> bool:
        url = f"{panorama_url}/restapi/v10.2/Panorama/Templates"
        headers = {"Content-Type": "application/json", 'X-PAN-KEY': f"{api_key}"}
        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        return False

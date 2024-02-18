import os
from xml.etree import ElementTree

import requests


class APICall:

    @staticmethod
    def get_api_key(panorama_url, user, password):
        user = user
        password = password
        key_response = requests.get(url=f"{panorama_url}/api/?type=keygen&user={user}&password={password}",
                                    verify=False)
        xml_key = key_response.content.decode('utf-8')
        root = ElementTree.fromstring(xml_key)
        apikey = root.find(".//key").text
        return apikey

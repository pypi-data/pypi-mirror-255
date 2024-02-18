# def create_zone_if_not_exist(panorama_tool_url, apikey, zone):
#     if zone not in get_zones(panorama_tool_url, apikey):
#         url = f"{panorama_url}/restapi/v10.2/Network/Zones"
#         params = {'name': zone, 'location': 'template', 'template': 'TestTemplate', 'vsys': "test"}
#         payload = {'name': zone, 'location': 'template', 'template': 'TestTemplate'}
#         headers = {"Content-Type": "application/json",
#                    'X-PAN-KEY': f"{apikey}"}
#         response = requests.post(url=url, headers=headers, params=params, data=json.dumps(payload), verify=False)
#         zones = json.loads(response.content.decode('utf-8'))
#         return zones
#     else:
#         return "Already exists."
#
# def get_zones(panorama_url, apikey):
#     url = f"{panorama_url}/restapi/v10.2/Network/Zones"
#     params = {'location': 'template', 'template': 'TestTemplate', 'vsys': "vsys1"}
#     headers = {"Content-Type": "application/json",
#                'X-PAN-KEY': f"{apikey}"}
#     response = requests.get(url=url, headers=headers, params=params, verify=False)
#     zones = json.loads(response.content.decode('utf-8'))
#     return zones
# def get_zone_payload(zone_name, zone_type, description=""):
#     zone_payload = {
#         "name": zone_name,
#         "zone_type": zone_type,
#         "description": description
#     }
#     return zone_payload

# if __name__ == "__main__":
    # response = get_zones(panorama_url=panorama_url, apikey=apikey)
    # response = create_zone_if_not_exist(panorama_url=panorama_url, apikey=apikey, zone="Zone_11")
    # response = create_zone_if_not_exist(panorama_url=panorama_url, apikey=apikey, zone="Transfer")

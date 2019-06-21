#!/usr/bin/env python3

import requests

base_url = 'https://api.meraki.com/api/v0'


# List the organizations that the user has privileges on
# https://api.meraki.com/api_docs#list-the-organizations-that-the-user-has-privileges-on
def get_user_orgs(api_key):
    get_url = f'{base_url}/organizations'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = requests.get(get_url, headers=headers)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# List the networks in an organization
# https://api.meraki.com/api_docs#list-the-networks-in-an-organization
def get_networks(api_key, org_id, configTemplateId=None):
    get_url = f'{base_url}/organizations/{org_id}/networks'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    if configTemplateId:
        get_url += f'?configTemplateId={configTemplateId}'

    response = requests.get(get_url, headers=headers)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Enable/Disable VLANs for the given network
# https://api.meraki.com/api_docs#enable/disable-vlans-for-the-given-network
def enable_vlans(api_key, net_id, enabled=True):
    put_url = f'{base_url}/networks/{net_id}/vlansEnabledState'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    payload = {'enabled': enabled}

    response = requests.put(put_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Create a network
# https://api.meraki.com/api_docs#create-a-network
def create_network(api_key, org_id, name, net_type='wireless', tags='', copyFromNetworkId=None, timeZone='America/Los_Angeles'):
    post_url = f'{base_url}/organizations/{org_id}/networks'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    if tags and type(tags) == list:
        tags = ' '.join(tags)

    vars = locals()
    params = ['name', 'tags', 'timeZone', 'copyFromNetworkId']
    payload = dict((k, vars[k]) for k in params)
    payload['type'] = net_type

    response = requests.post(post_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Delete a network
# https://api.meraki.com/api_docs#delete-a-network
def delete_network(api_key, net_id):
    delete_url = f'{base_url}/networks/{net_id}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = requests.delete(delete_url, headers=headers)
    return response.ok


# Blink the LEDs on a device
# https://api.meraki.com/api_docs#blink-the-leds-on-a-device
def blink_device(api_key, net_id, serial, duration=20, period=160, duty=50):
    post_url = f'{base_url}/networks/{net_id}/devices/{serial}/blinkLeds'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    vars = locals()
    params = ['duration', 'period', 'duty']
    payload = dict((k, vars[k]) for k in params)

    response = requests.post(post_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Generate a snapshot of what the camera sees at the specified time and return a link to that image.
# https://api.meraki.com/api_docs#generate-a-snapshot-of-what-the-camera-sees-at-the-specified-time-and-return-a-link-to-that-image
def take_snapshot(api_key, net_id, serial, timestamp=None):
    post_url = f'{base_url}/networks/{net_id}/cameras/{serial}/snapshot'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'} if timestamp else {'X-Cisco-Meraki-API-Key': api_key}

    payload = {'timestamp': timestamp} if timestamp else {}

    response = requests.post(post_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Send a message in Webex Teams
def post_message(url, message):
    # Webex Teams bot token
    token = ''
    # Teams account email
    email = ''

    headers = {'content-type': 'application/json; charset=utf-8', 'authorization': f'Bearer {token}'}
    payload = {'toPersonEmail': email, 'file': url, 'markdown': message}
    requests.post('https://api.ciscospark.com/v1/messages/', headers=headers, json=payload)

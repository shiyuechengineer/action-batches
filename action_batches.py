#!/usr/bin/env python3

import time

import requests

base_url = 'https://api.meraki.com/api/v0'


def create_action_batch(api_key, org_id, confirmed=False, synchronous=False, actions=None):
    post_url = f'{base_url}/organizations/{org_id}/actionBatches'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    payload = {
        'confirmed': confirmed,
        'synchronous': synchronous,
        'actions': actions,
    }

    response = requests.post(post_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


def get_org_action_batches(api_key, org_id):
    get_url = f'{base_url}/organizations/{org_id}/actionBatches'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = requests.get(get_url, headers=headers)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


def get_action_batch(api_key, org_id, batch_id):
    get_url = f'{base_url}/organizations/{org_id}/actionBatches/{batch_id}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = requests.get(get_url, headers=headers)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


def delete_action_batch(api_key, org_id, batch_id):
    delete_url = f'{base_url}/organizations/{org_id}/actionBatches/{batch_id}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = requests.delete(delete_url, headers=headers)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


def update_action_batch(api_key, org_id, batch_id, confirmed=False, synchronous=False):
    put_url = f'{base_url}/organizations/{org_id}/actionBatches/{batch_id}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    payload = {
        'confirmed': confirmed,
        'synchronous': synchronous,
    }

    response = requests.post(put_url, headers=headers, json=payload)
    data = response.json() if response.ok else response.text
    return (response.ok, data)


# Helper function to check the completion status of an asynchronous action batch
def check_status(api_key, org_id, batch_id):
    (ok, data) = get_action_batch(api_key, org_id, batch_id)
    if ok and data['status']['completed'] and not data['status']['failed']:
        print(f'Action batch {batch_id} completed!')
        return 1
    elif ok and data['status']['failed']:
        print(f'Action batch {batch_id} failed with errors {data["status"]["errors"]}!')
        return -1
    else:
        return 0


# Check until asynchronous action batch either completes or fails
def check_until_completed(api_key, org_id, batch_id, print_message=False):
    counter = 0
    while True:
        status = check_status(api_key, org_id, batch_id)
        if status == 1:
            return True
        elif status == -1:
            return False
        elif print_message:
            print(f'Action batch {batch_id} processing... ({99 - counter} bottles of beer)')
            time.sleep(1)
            counter += 1

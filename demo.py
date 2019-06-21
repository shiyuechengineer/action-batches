#!/usr/bin/env python3

import csv
import json
from json.decoder import JSONDecodeError
import os
import random
import time
import sys

from dashboard import *
from action_batches import *
from group_policies import policies


# Create networks using action batches
def create_networks(api_key, org_id, sites, locations, custom_tags):
    net_type = 'appliance switch wireless camera systemsManager'
    (ok, networks) = get_networks(api_key, org_id)
    net_names = [net['name'] for net in networks]
    try:
        isp_net = networks[net_names.index('ISP')]['id']
    except ValueError:
        (ok, data) = create_network(api_key, org_id, 'ISP', net_type)
        if not ok:
            sys.exit(data)
        isp_net = data['id']
        (ok, data) = enable_vlans(api_key, isp_net, True)
        if not ok:
            sys.exit(data)
        print(f'Created a base network "ISP" with VLANs enabled, network ID {isp_net}!')

    actions = []
    for (site, location) in zip(sites, locations):
        net_name = location.replace(',', ' -')
        net_tags = ' '.join(random.sample(custom_tags + ['foo', 'bar', 'foobar', 'spam', 'ham', 'eggs'], 3))
        action = {
            'name': net_name,
            'type': net_type,
            'tags': net_tags,
            'copyFromNetworkId': isp_net
        }
        actions.append({
            'resource': f'/organizations/{org_id}/networks',
            'operation': 'create',
            'body': action
        })

    with open('create_networks.json', 'w') as fp:
        payload = {
            'confirmed': True,
            'synchronous': True,
            'actions': actions
        }
        json.dump(payload, fp)

    print('POSTing one synchronous action batch to create networks, payload in create_networks.json')
    (ok, data) = create_action_batch(api_key, org_id, True, True, actions)
    if not ok:
        sys.exit(data)
    else:
        batch_id = data['id']
        print(f'Action batch {batch_id} completed!')
    # input('Hit ENTER once manual POST is successful...')


# Helper function to claim devices
def add_devices(actions, net_id, serial):
    if serial:
        actions.append(
            {
                'resource': f'/networks/{net_id}/devices',
                'operation': 'claim',
                'body': {
                    'serial': serial
                }
            }
        )


# Create/claim devices using action batches
def create_devices(api_key, org_id, actions):
    with open('create_devices.json', 'w') as fp:
        payload = {
            'confirmed': True,
            'synchronous': False,
            'actions': actions
        }
        json.dump(payload, fp)

    print('POSTing one asynchronous action batch to claim devices, payload in create_devices.json')
    (ok, data) = create_action_batch(api_key, org_id, True, False, actions)
    if not ok:
        print(data)
    else:
        batch_id = data['id']
        done = check_until_completed(api_key, org_id, batch_id)
    # input('Hit ENTER once manual POST is successful...')


# Helper function to configure devices' attributes
def configure_device(actions, net_id, serial, name, address, user_name, custom_tags):
    if serial:
        actions.append(
            {
                'resource': f'/networks/{net_id}/devices/{serial}',
                'operation': 'update',
                'body': {
                    'name': name,
                    'tags': ' '.join(random.sample(custom_tags + ['foo', 'bar', 'foobar', 'spam', 'ham', 'eggs'], 3)),
                    'address': address,
                    'moveMapMarker': True,
                    'notes': f'installed by {user_name}'
                }
            }
        )


# Helper function configure devices' management IP addresses
def batch_devices(actions, net_id, serials_ips, vlan):
    for (serial, ip) in serials_ips:
        if serial:
            action = {
                'resource': f'/networks/{net_id}/devices/{serial}/managementInterfaceSettings',
                'operation': 'update',
                'body': {
                    'wan1': {
                        'usingStaticIp': True,
                        'vlan': vlan if '.2' in ip else '',  # no VLAN tag for AP
                        'staticIp': ip,
                        'staticGatewayIp': ip[:-1] + '1',  # strip last digit, and use MX which is .1
                        'staticSubnetMask': '255.255.255.0',
                        'staticDns': ['208.67.220.220', '208.67.222.222'],
                    }
                }
            }
            actions.append(action)


# Helper function configure MX VLANs
def batch_vlans(actions, net_id, num):
    # Update or delete default VLAN1, depending on site
    if num == '0':
        actions.append({
            'resource': f'/networks/{net_id}/vlans/1',
            'operation': 'update',
            'body': {
                'name': f'Site {num} - Management',
                'subnet': f'10.{num}.1.0/24',
                'applianceIp': f'10.{num}.1.1'
            }
        })
    else:
        actions.append({
            'resource': f'/networks/{net_id}/vlans/1',
            'operation': 'destroy',
            'body': {}
        })

    # Add more VLANs
    for (x, name) in zip(range(1, 5), ['Management', 'Data', 'Voice', 'Guest']):
        if (num == '0' and x == 1) or (num != '0' and x == 4):
            continue
        vlan = int(num + str(x))
        body = {
            'id': f'{vlan}',
            'name': f'Site {num} - {name}',
            'subnet': f'10.{num}.{x}.0/24',
            'applianceIp': f'10.{num}.{x}.1'
        }
        action = {
            'resource': f'/networks/{net_id}/vlans',
            'operation': 'create',
            'body': body
        }
        actions.append(action)


# Helper function to configure group policies
def batch_policies(actions, net_id):
    names = ['Employee', 'Executive', 'Guest', 'Sales', 'Support']
    for name in names:
        body = policies[name]
        body['name'] = name
        action = {
            'resource': f'/networks/{net_id}/groupPolicies',
            'operation': 'create',
            'body': body
        }
        actions.append(action)


# Helper function to configure MS switchports
def batch_switchports(actions, switch, num, vlan, custom_tags):
    if switch:
        for x in range(1, 10):
            body = {}
            if x == 1:
                body = {
                    'name': 'Uplink to MX',
                    'type': 'trunk',
                    'vlan': vlan,
                }
            elif x == 3:
                body = {
                    'name': 'MR wireless AP',
                    'type': 'trunk',
                    'vlan': vlan,
                }
            elif x == 5:
                body = {
                    'name': 'MV security camera',
                    'type': 'trunk',
                    'vlan': vlan,
                }
            elif x == 7:
                body = {
                    'name': 'ready to connect!',
                    'type': 'access',
                    'vlan': random.choice(range(vlan + 1, vlan + 4)),
                }
            elif x == 9:
                body = {
                    'name': 'SFP port',
                    'type': 'trunk',
                    'vlan': vlan,
                }
            else:
                continue
            body['tags'] = ' '.join(random.sample(custom_tags + ['foo', 'bar', 'foobar', 'spam', 'ham', 'eggs'], 3))
            action = {
                'resource': f'/devices/{switch}/switchPorts/{x}',
                'operation': 'update',
                'body': body
            }
            actions.append(action)


# Create/configure settings using action batches
def create_settings(api_key, org_id, actions, counter):
    with open(f'create_settings_{counter}.json', 'w') as fp:
        payload = {
            'confirmed': True,
            'synchronous': True,
            'actions': actions
        }
        json.dump(payload, fp)

    print(f'POSTing one synchronous action batch to configure settings, payload in create_settings_{counter}.json')
    (ok, data) = create_action_batch(api_key, org_id, True, True, actions)
    if not ok:
        if len(data) < 10 ** 3:
            print(data)
    else:
        batch_id = data['id']
        if data['status']['completed']:
            print(f'Action batch {batch_id} completed!')
        elif data['status']['failed']:
            print(f'Action batch {batch_id} failed with errors {data["status"]["errors"]}!')

    # done = check_until_completed(api_key, org_id, batch_id)


def main():
    # Get user's API key and check org access
    while True:
        api_key = input('Enter your Meraki dashboard API key: ')
        (ok, orgs) = get_user_orgs(api_key)
        if ok:
            break
        else:
            print('That API key is either incorrect, or just created so wait a few moments please!')

    # Get organization ID
    org_ids = []
    print('That API key has access to these organizations with IDs & names, respectively:')
    for org in orgs:
        org_id = org["id"]
        org_ids.append(str(org_id))
        print(f'{org_id:18}\t{org["name"]}')
    print()
    while True:
        org_id = input('Enter in the organization ID: ')
        if org_id in org_ids:
            break
        else:
            print('That org ID is not one listed, try again!')
    print()

    # Get name and custom tags
    user_name = input('Enter in your name(s): ')
    custom_tags = input('Enter in some optional custom tag(s): ')
    custom_tags = custom_tags.split()

    # Create some stuff
    while True:
        print()
        stop = input('Create which of the following?  1) Networks   2) Devices   3) Settings   4) Fun!   5 ) Bye!  ')
        stop = stop.lower()
        if 'network' in stop:
            stop = '1'
        elif 'device' in stop:
            stop = '2'
        elif 'setting' in stop:
            stop = '3'
        elif 'fun' in stop:
            stop = '4'
        elif 'fun' in stop:
            stop = '5'

        try:
            with open('networks_data.json') as fp:
                networks_data = json.load(fp)
        except (FileNotFoundError, JSONDecodeError):
            networks_data = []

        # Creating networks
        if stop == '1':
            if networks_data:
                print('Networks already created, since networks_data.json exists!')
            else:
                with open('inventory.csv', newline='\n', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
                    sites = []
                    locations = []
                    for row in reader:
                        site = row['Site']
                        location = row['Location']
                        sites.append(site)
                        locations.append(location)

                    create_networks(api_key, org_id, sites, locations, custom_tags)

                    networks_data = []
                    (ok, data) = get_networks(api_key, org_id)
                    if not ok:
                        sys.exit(data)
                    else:
                        networks = data
                    net_names = [network['name'] for network in networks]
                    for (site, location) in zip(sites, locations):
                        net_name = location.replace(',', ' -')
                        if net_name in net_names:
                            net_id = networks[net_names.index(net_name)]['id']
                            networks_data.append({'net_id': net_id, 'location': location, 'site': site})
                    with open('networks_data.json', 'w') as fp:
                        json.dump(networks_data, fp)
                    print('Log file networks_data.json updated!')

        # Creating devices
        elif stop == '2':
            if not networks_data:
                print('Networks need to be created first!')
            else:
                with open('inventory.csv', newline='\n', encoding='utf-8-sig') as csvfile:
                    counter = 0
                    actions = []
                    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
                    for row in reader:
                        net_id = networks_data[counter]['net_id']
                        mx_serial = row['MX device']
                        ms_serial = row['MS device']
                        mr_serial = row['MR device']
                        mv_serial = row['MV device']
                        mgmt_vlan = int(row['Mgmt. VLAN'])
                        for serial in (mx_serial, ms_serial, mr_serial, mv_serial):
                            add_devices(actions, net_id, serial)
                        devices = [(mx_serial, 'SD-WAN UTM gateway'),
                                   (ms_serial, 'Access switch'),
                                   (mr_serial, 'Wireless AP'),
                                   (mv_serial, 'Security camera')]
                        networks_data[counter]['devices'] = devices
                        networks_data[counter]['mgmt_vlan'] = mgmt_vlan
                        counter += 1

                    create_devices(api_key, org_id, actions)

                    with open('networks_data.json', 'w') as fp:
                        json.dump(networks_data, fp)
                    print('Log file networks_data.json updated!')

        # Creating settings
        elif stop == '3':
            if not networks_data:
                print('Networks need to be created first!')
            elif 'devices' not in networks_data[0]:
                print('Devices need to be claimed first!')
            else:
                with open('inventory.csv', newline='\n', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
                    counter = 0
                    for row in reader:
                        actions = []
                        net_id = networks_data[counter]['net_id']
                        mx_serial = row['MX device']
                        ms_serial = row['MS device']
                        mr_serial = row['MR device']
                        mv_serial = row['MV device']
                        mgmt_vlan = int(row['Mgmt. VLAN'])
                        site = networks_data[counter]['site']
                        location = networks_data[counter]['location']
                        address = row['Address'] if 'Address' in row else location

                        devices = [(mx_serial, 'SD-WAN UTM gateway'),
                                   (ms_serial, 'Access switch'),
                                   (mr_serial, 'Wireless AP'),
                                   (mv_serial, 'Security camera')]
                        for (device, description) in devices:
                            configure_device(actions, net_id, device, description, address, user_name, custom_tags)

                        # Configure management IP addresses (uplink interfaces) via action batch
                        batch_devices(actions, net_id, [(ms_serial, row['MS IP']), (mr_serial, row['MR IP'])], mgmt_vlan)

                        # Batch more settings
                        settings_created = 'settings_created' in networks_data[counter]
                        if not settings_created:
                            batch_vlans(actions, net_id, site)  # create VLANs
                            batch_policies(actions, net_id)  # create group policies
                        batch_switchports(actions, ms_serial, site, mgmt_vlan, custom_tags)  # configure switch ports

                        create_settings(api_key, org_id, actions, counter)
                        networks_data[counter]['settings_created'] = True
                        counter += 1
                        time.sleep(10)

                    with open('networks_data.json', 'w') as fp:
                        json.dump(networks_data, fp)

        # Creating fun!
        elif stop == '4':
            if not networks_data:
                print('Networks need to be created first!')
            elif 'devices' not in networks_data[0]:
                print('Devices need to be claimed first!')
            else:
                with open('inventory.csv', newline='\n', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
                    row = next(reader)
                    stage_net = networks_data[0]['net_id']
                    stage_devices = networks_data[0]['devices']
                    stage_cam = networks_data[0]['devices'][3][0]

                    for (device, description) in stage_devices:
                        (ok, data) = blink_device(api_key, stage_net, device, 120)
                    if ok:
                        print(f'Devices should now be blinking!')

                    # Take a snapshot from on-stage camera
                    time.sleep(5)
                    for x in range(3):
                        if x == 0:
                            message = '## 🎉🥂 Thank you for attending _Powerful, Programmable Cloud Networking with Meraki APIs_! 💪📝'
                        elif x == 1:
                            message = '## ✅😇 Check out the Developer Hub @ meraki.io! 🌎💚'
                        elif x == 2:
                            message = '## 🌟💫 Hope you enjoyed this demo, and thanks for watching! 🤜🤛'

                        (ok, data) = take_snapshot(api_key, stage_net, stage_cam)
                        if ok:
                            print(message)
                            photo = data['url']
                            time.sleep(10)
                            post_message(photo, message)

        # Bye!
        elif stop == '5':
            for net in networks_data:
                ok = delete_network(api_key, net['net_id'])
                if ok:
                    net_name = net["location"].replace(',', '-')
                    print(f'Network {net_name} deleted!')
            if os.path.exists('networks_data.json'):
                os.remove('networks_data.json')
            sys.exit('Take care!')


if __name__ == '__main__':
    main()

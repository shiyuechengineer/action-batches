policies = {
    'Employee': {
        'bandwidth': {
            'settings': 'custom',
            'bandwidthLimits': {
                'limitUp': 5120,
                'limitDown': 10240
            }
        }
    },
    'Executive': {
        'bandwidth': {
            'settings': 'ignore'
        },
        'firewallAndTrafficShaping': {
            'settings': 'custom',
            'trafficShapingRules': [
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/16',
                                'name': 'VoIP & video conferencing'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'ignore'
                    },
                    'dscpTagValue': 46,
                    'priority': 'high'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/20',
                                'name': 'Remote monitoring & management'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 34,
                    'priority': 'normal'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/7',
                                'name': 'Online backup'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 10,
                    'priority': 'low'
                }
            ]
        }
    },
    'Guest': {
        'scheduling': {
            'enabled': True,
            'monday': {
                'active': True,
                'from': '08:00',
                'to': '17:00'
            },
            'tuesday': {
                'active': True,
                'from': '08:00',
                'to': '17:00'
            },
            'wednesday': {
                'active': True,
                'from': '08:00',
                'to': '17:00'
            },
            'thursday': {
                'active': True,
                'from': '08:00',
                'to': '17:00'
            },
            'friday': {
                'active': True,
                'from': '08:00',
                'to': '17:00'
            },
            'saturday': {
                'active': False,
                'from': '00:00',
                'to': '24:00'
            },
            'sunday': {
                'active': False,
                'from': '00:00',
                'to': '24:00'
            }
        },
        'firewallAndTrafficShaping': {
            'settings': 'custom',
            'trafficShapingRules': [
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/13',
                                'name': 'Video & music'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 28,
                    'pcpTagValue': 2
                }
            ],
            'l3FirewallRules': [
                {
                    'comment': 'no access to internal stuff',
                    'policy': 'deny',
                    'protocol': 'any',
                    'destPort': 'Any',
                    'destCidr': '10.0.0.0/8'
                },
                {
                    'comment': 'no access to FQDNs',
                    'policy': 'deny',
                    'protocol': 'any',
                    'destPort': 'Any',
                    'destCidr': 'xyz.com'
                }
            ],
            'l7FirewallRules': [
                {
                    'policy': 'deny',
                    'type': 'applicationCategory',
                    'value': {
                        'id': 'meraki:layer7/category/8',
                        'name': 'Peer-to-peer (P2P)'
                    }
                }
            ]
        },
        'contentFiltering': {
            'allowedUrlPatterns': {
                'settings': 'append',
                'patterns': [
                    'meraki.com',
                    'cisco.com'
                ]
            },
            'blockedUrlPatterns': {
                'settings': 'append',
                'patterns': [
                    'mancity.com'
                ]
            },
            'blockedUrlCategories': {
                'settings': 'append',
                'categories': [
                    'meraki:contentFiltering/category/11',
                    'meraki:contentFiltering/category/62'
                ]
            }
        },
        'vlanTagging': {
            'settings': 'network default',
            'vlanId': '4'
        }
    },
    'Sales': {
        'bandwidth': {
            'settings': 'custom',
            'bandwidthLimits': {
                'limitUp': 10240,
                'limitDown': 10240
            }
        },
        'firewallAndTrafficShaping': {
            'settings': 'custom',
            'trafficShapingRules': [
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/16',
                                'name': 'VoIP & video conferencing'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'ignore'
                    },
                    'dscpTagValue': 46,
                    'priority': 'high'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/20',
                                'name': 'Remote monitoring & management'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 34,
                    'priority': 'normal'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/7',
                                'name': 'Online backup'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 10,
                    'priority': 'low'
                }
            ]
        }
    },
    'Support': {
        'bandwidth': {
            'settings': 'ignore'
        },
        'firewallAndTrafficShaping': {
            'settings': 'custom',
            'trafficShapingRules': [
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/16',
                                'name': 'VoIP & video conferencing'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'ignore'
                    },
                    'dscpTagValue': 46,
                    'priority': 'high'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/20',
                                'name': 'Remote monitoring & management'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 34,
                    'priority': 'normal'
                },
                {
                    'definitions': [
                        {
                            'type': 'applicationCategory',
                            'value': {
                                'id': 'meraki:layer7/category/7',
                                'name': 'Online backup'
                            }
                        }
                    ],
                    'perClientBandwidthLimits': {
                        'settings': 'network default'
                    },
                    'dscpTagValue': 10,
                    'priority': 'low'
                }
            ]
        }
    }
}
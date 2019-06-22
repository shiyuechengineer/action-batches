# Demo of Meraki Dashboard API action batches 

The source code provided in this repository shows a full, interactive demo of [action batches](https://developer.cisco.com/meraki/api/#/rest/guides/action-batches), a Meraki Dashboard API mechanism for submitting batched configuration requests in a single synchronous or asynchronous transaction. Using the files here, you'll be able to:

- import sites & locations specified in [inventory.csv](./inventory.csv), which is the only file that needs to be edited
- create networks based on those location names
- claim devices into each of those networks (using your own device serial numbers)
- configure settings, such as device attributes, group policies, VLANs, switchports, & management IP addresses

These steps are performed via action batches, and sample JSON files are generated through the process.

### Steps to get started

- Clone or download this repo
- Edit [inventory.csv](./inventory.csv) such that it includes information about your sites, locations, and devices
- Start the demo by running `python[3] demo.py`

To see an example, watch the [Action Batches Demo.mp4](./Action\ Batches\ Demo.mp4) video.

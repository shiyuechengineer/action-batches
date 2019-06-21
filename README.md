# Demo of Meraki dashboard API action batches

The source code provided in this repository shows a full, interactive demo of Meraki dashboard API's [action batches](https://developer.cisco.com/meraki/api/#/rest/guides/action-batches). Using the files here, you'll be able to:
- import in sites & locations specified in _inventory.csv_, which is the only file that needs to be edited
- create networks based on those location names
- claim devices into each of those networks (using your own device serial numbers)
- configure settings, such as device attributes, group policies, VLANs, switchports, & management IP addresses

These steps are performed via action batches, and sample JSON files are generated through the process.

#### After downloading all files here and editing _inventory.csv_, start the demo by running **python[3] demo.py**. Also for an example, watch the **Action Batches Demo.mp4** video.

# Linode Functions - linode.py
## Remote Update
```python
remote_update(confg,keyfile)
```
**- config:** is a config section fromt he config file.

**- keyfile:** is the SSH keyfile required for authentication to remote machine.

This function runs the remote_updates.py scripts on the specified remote machine.

## Wait for completion
```python
wait_for_completion(polling_thread)
```

**- polling_thread:** must be a polling thread object from the linode_api4 module

This function waits for completion of the action that the event poller was configured to watch for.

## Get Type Label
```python
get_type_label(api_client, id)
```

**- api_client:** a linode_api client object

**- id:** The type ID to query for a label

This finction queries the list of linode types and returns the label for the given ID.

## Wait for running
#### Needs work
```python
wait_for_running(api_client, linode_id, linode_name)
```

**- api_client:** a linode_api client object

**- linode_id:** ID of the linode to watch

**- linode_name:** Name of the linode instance to watch

This function will wait until the status of the given linode instance is 'running'

## Rename Linode Instance
```python
rename_linode_instance(instance, new_name)
```

**- instance:** the linode instance to be renamed

**- new_name:** The new name for the instance

This function simply renames a given linode instnace

## Create New Linode Instance
```python
create_linode_instance(api_client, plan, region, image, linode_username, label, root_password, firewall, stackscript, booted)
```
**- api_client:** The linode_api4.Api object to use for making API calls.

**- plan:** The Linode plan ID specifying the resources for the new instance.

**- region:** The Linode region ID where the new instance will be created.

**- image:** The Linode image ID to use for the new instance.

**- linode_username:** Linode user that can access the instance. Assigns SSH Key

**- label:** The label for the new Linode instance.

**- root_password:** The root password for the new Linode instance.

**- firewall:** Optional firewall ID to assign to the new Linode instance.

**- stackscript:** Optional Stackscript ID to assign to the new Linode Instance

**- booted:** Optional Bool to keep instance powered off after provisioning

This function creates a new linode instance. Returns A linode_api4.Instance object representing the newly created Linode instance.

## Get SSH Key ID by label
```python
get_ssh_key_id_by_label(api_client, ssh_key_label)
```
Get the ID of an SSH key based on its label.

**- api_client:** The linode_api4.Api object to use for making API calls.

**- ssh_key_label:** The label of the SSH key.

**- return:** The ID of the SSH key, or None if not found.

## Get Firewall ID by Label
```python
get_firewall_id_by_label(api_client, firewall_label):
```

Get the ID of a firewall based on its label.

**- api_client:** The linode_api4.Api object to use for making API calls.

**- firewall_label:** The label of the firewall.

**- return:** The ID of the firewall, or None if not found.

## Get Stackscript id by Label and Username
```python
get_stackscript_id_by_label_and_username(api_client, stackscript_label, stackscript_username)
```

Get the ID of a StackScript based on its label and username.

**- api_client:** The linode_api4.Api object to use for making API calls.

**- stackscript_label:** The label of the StackScript.

**- stackscript_username:** The username associated with the StackScript.

**- return:** The ID of the StackScript, or None if not found.

## Detach all Volumes
```python
detach_all_volumes(instance)
```

Detaches all volumes from a given linode instance

**- instance:** The linode instance to detach all volumes from

## Attach Volume
```python
attach_volume(api_client, volume_label, instance)
```

Attach a persistent volume to an instance

**- api_client:** The linode_api4 client object to be used to run the API command

**- volume_label:** The label of the volume to be attached

**- instance:** The linode instance that the volume should be attached to.

## Wait for Instance State
### Needs work, refer to wait for running
```pythgon
wait_for_instance_state(api_client, linode_id, linode_name, required_state='running')
```

Checks the given linode instance and waits for the required status

**- api_client:** The linode_api4 client object to be used to check the status of the instance

**- linode_id:** the ID of the linode instance to check

**- linode_name:** The name of the linode instance to check

**- required_state:** Default value is 'running'

## Swap IPv4 Addresses
#### Improvment: Change instnace1 and 2 from 2 seperate varaiables into an array and parse that int he function
```python
swap_ipv4_addresses(api_client, instance1, instance2)
```

Swaps IPv4 address between 2 different linode instances

**- api_client:** The linode_api4 client object to be used to make the swap

**- instance1:** The first linode instance to have its IP swapped

**- instance2:** The second linode instance to have its IP swapped
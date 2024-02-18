<a id="user-guide"></a>
A python wrapper for UO-NetDot's RESTful API.

* [Changelog](./changelog.md)
* [API Documentation](./generated-api-docs.md)
* [ENV VARs Documentation](./generated-env-var-docs.md)

> ℹ This documentation is targeted for Network Engineers (who want to do more work using Python).
> There are ***Examples** below that can help you get started **(copy-paste friendly)!***
>
> No particular Python knowledge is required (though there is plenty of "Python tip"s and tricks to be learned here)!
> 
> **⚠ NOTE:** From 0.2.0 onward, this API wrapper user support for the [de facto Open Source version of NetDot (GitHub)](https://github.com/cvicente/Netdot) (today, we hope it will work for you with limited warnings).

[![PyPI version](https://badge.fury.io/py/netdot.svg)](https://pypi.org/project/netdot/)

<!-- These need to be uploaded somewhere visible to the internet for us to use them on pypi.org... Time for a github repository I'm thinking!

![Code Coverage](assets/coverage.svg)
![Test Suite](assets/tests.svg)
-->

# Install 

This package is deployed to pypi.org.
Download and install it with `pip`:

```sh
pip install netdot
```


# Interactive Usage (Python interpreter)

Before getting into building a massive integration/tool, you might jump in and get some experience.
Thankfully, we have the [Python Interpreter (external)](https://docs.python.org/3/tutorial/interpreter.html) where we can jump in and do some testing!

```sh
# Enter the Python interpreter by running just "python" in your shell
$ python
Python 3.8.10 (default, May 26 2023, 14:05:08)     
... omitted for brevity...
>>> import netdot
>>>
```


With the netdot package imported, you can proceed with setting up a connecting and downloading some data!

> ℹ Most of the [Python Netdot API](./generated-api-docs.md) is actually runtime-generated code.
>
> Use **tab completion** to quickly learn what methods are available.

> ℹ The Python interpreter is often referred to as 'a REPL' (Read-Eval-Print-Loop).
> For more info, see ["Using the REPL (in VSCode)" documentation (external)](https://www.learnpython.dev/01-introduction/02-requirements/05-vs-code/04-the-repl-in-vscode/).


<a id=connecting-in-the-interpreter-netdotconnect></a>

## Connecting in the interpreter: `netdot.connect()`

We have enabled interpreter-usage as a first-class feature.
In particular, you will want to use the `connect` function like the following.

```python
>>> import netdot
>>> nd_repo = netdot.connect()
What is the URL of the NetDot server? [https://nsdb.uoregon.edu]: ('enter' to use default)
NetDot username: myusername
NetDot password: ********** (using getpass module, to securely collect password)
>>> 
```

We now have a `netdot.Repository` named `nd_repo` connected to Netdot!

> ℹ `netdot.connect()` returns a `netdot.Repository` instance with `propose_changes` enabled by default (AKA 'dry run' feature).

### Example 1: Get Location of an IP Address (by Subnet)

If Netdot has well maintained SiteSubnet relationships, then you can use this feature to quickly look up which Site (Building) holds an IP Address.


1. Get the IPBlock for the IP Address:
```python
>>> ipblock = nd_repo.get_ipblock_by_address('128.123.25.41')
```
2. Get the Subnet IPBlock via `load_parent`:
> ℹ Similar to `load_parent`, there is also a `load_children` method.
```python
>>> subnet = ipblock.load_parent()
```
3. Call `load_sites` on the subnet to load any/all sites that are related to this subnet (via SiteSubnet relationships):
> ℹ If your Netdot Subnet stretches across many Netdot Sites, this will return all of those Sites.
```python
>>> subnet.load_sites()
[Site(id=42, name='Oregon Hall'... )]
```

#### Example 1: Code Sample (copy-paste friendly)

```python
ipblock = nd_repo.get_ipblock_by_address('128.123.25.41')
subnet = ipblock.load_parent()
subnet.load_sites()
```

### Example 2: Lookup DNS Record by IP Address

You can use this API to lookup (and modify) the DNS Resource Record (RR) associated to some IP Address.

```python
>>> dns_RR_record = nd_repo.get_rr_by_address('10.243.14.32')
```

The RR contains several pieces of information that may be useful to review!


1. You might wanna see what the Fully Qualified Domain Name (FQDN) is for this RR.
```python
>>> dns_RR_record.infer_FQDN()
'foobar.uoregon.edu'
```
2. You can look at the RR's info (AKA 'comment'):
```python
>>> dns_RR_record.info
'LOC: 123 FooBar Hall CON: Jenny J, 867-5309'
```
3. You can check when this RR was created, and last modified:
```python
>>> dns_RR_record.created
datetime.datetime(2020, 1, 16, 12, 7, 50)
>>> dns_RR_record.modified
datetime.datetime(2020, 1, 16, 12, 7, 50)
```
4. You can propose an update to the name if you like:
> ℹ You can make updates *any* of the fields of `dns_RR_record`.
```python
>>> dns_RR_record.name = 'bazzle'
Will UPDATE RR: RR(id=265246, active=True, auto_update=False, expiration='', info='', name='bazzle',...
```
5. And save those the name change to Netdot by calling `save_changes()`
```python
>>> nd_repo.save_changes()
```

#### Example 2: Code Sample (copy-paste friendly)

```
dns_RR_record = nd_repo.get_rr_by_address('10.243.14.32')
dns_RR_record.infer_FQDN()
dns_RR_record.info
dns_RR_record.created
dns_RR_record.modified
dns_RR_record.name = 'bazzle'
# And save the name change using:
# nd_repo.save_changes()
```

### Example 3: Pretty Printing DNS Records

*Continuing from the prior example,* assume we just want to review all the details for the DNS Records we just retrieved.

6. Import `pprint` from the "pprint" module (part of Python stdlib)
```python
>>> from pprint import pprint
```
7. Use the `pprint` function to print **any** returned Netdot objects
```python
>>> pprint(dns_RR_record)
RR(id=54482,
   active=True,
   auto_update=False,
   expiration='',
   info='LOC: 215A Oregon Hall CON: Chris LeBlanc, 6-2931 ',
   name='metadata2',
   zone='uoregon.edu',
   zone_xlink=1,
   created=datetime.datetime(2020, 1, 16, 12, 7, 50),
   modified=datetime.datetime(2020, 1, 16, 12, 7, 50))
>>> dns_RRADDRs = dns_RR_record.load_rraddr()
>>> pprint(dns_RRADDRs)
[RRADDR(id=16759,
        ipblock='128.223.37.93',
        ipblock_xlink=72430287,
        rr='metadata2.uoregon.edu',
        rr_xlink=54482,
        ttl='86400')]
```

#### Example 3: Code Sample (copy-paste friendly)

```
from pprint import pprint
pprint(dns_RR_record)
dns_RRADDRs = dns_RR_record.load_rraddr()
pprint(dns_RRADDRs)
```

### Example 4: Lookup Edge Port for MAC Address in NetDot

> ℹ Tip: This is useful for tracking down the physical location of some MAC Address.
>
>> **⚠ WARNING**: "find_edge_port" takes a LONG time, requires a LOT of HTTP requests, and includes assumptions that can lead to inconsistent and inaccurate results:
>>
>>Particularly, **if more than one forwarding table contains the MAC Address**, then NetDot will select the one whose forwarding table had the least entries.
>> 
>> This can be inaccurate especially if a 'forwarding table scan' is happening while you are trying to use `find_edge_port`.
>>
>> ℹ This assumption is present when looking up an edge port using NetDot's frontend as well. This method does require additional latency of HTTP requests, which is not required when using Netdot's frontend (frontend may have more accurate/consistent results).

You can use this API to lookup the Edge Port associated to some MAC Address.

```python
>>> interface = nd_repo.find_edge_port('8C3BADDA9EF1')
```

Once the interface lookup is complete (may take more than 60 seconds), it is very easy to check if there is any "`jack`" (location information) associated to this Interface!

```python
>>> interface.jack
'136A246B'
```

To load full details about the jack, instead call `load_jack()`

```python
>>> interface.load_jack()
HorizontalCable(id=6143, account='', closet='ASDF 101 Oregon Hall', ...)
```

#### Example 4: Code Sample (copy-paste friendly)

```
interface = nd_repo.find_edge_port('8C3BADDA9EF1')
interface.jack
interface.load_jack()
```

### Example 5: Check Devices Last ARP for a Site

Want to see the 'last ARP' time for all the devices that are located within the Site named "Death Star?"

1. First lookup the site:
```python
>>> site_name = 'Death Star'
>>> sites = nd_repo.get_sites_where(name=site_name)
>>> assert len(sites) == 1, f"Expected exactly one site with name {site_name}, found: {sites}"
>>> site = sites[0]
```
2. Then, simply call "load_devices" on that site:
```python
>>> devices = site.load_devices()
```
3. Print out the "last ARP" time for these devices (sorted). 
```python
>>> devices = sorted(devices, key=lambda device: device.last_arp)
>>> for device in devices:
>>>     print(f"{device.name} last ARPed at {device.last_arp}")
foo.uoregon.edu last ARPed at 1970-01-01 00:00:00
... trimmed for brevity...
bar.uoregon.edu last ARPed at 2023-10-20 15:00:03
baz.uoregon.edu last ARPed at 2023-11-07 20:00:04
foobar.uoregon.edu last ARPed at 2023-11-10 08:00:04
foobaz.uoregon.edu last ARPed at 2023-11-10 08:00:04
```

#### Example 5: Code Sample (copy-paste friendly)

```
site_name = 'Death Star'
sites = nd_repo.get_sites_where(name=site_name)
assert len(sites) == 1, f"Expected exactly one site with name {site_name}, found: {sites}"
site = sites[0]
devices = site.load_devices()
devices = sorted(devices, key=lambda device: device.last_arp)
for device in devices:
    print(f"{device.name} last ARPed at {device.last_arp}")
```

### Example 6: Delete All Devices for a Site

*Continuing from the last example,* imagine 'Death Star' has been fully removed from your campus (pesky rebels).

4. You need to delete all the devices associated to this site:
```python
>>> for device in devices:
>>>     device.delete()
```
5. The work has been prepared! Now, take a look at what changes will occur using either `show_changes` or `show_changes_as_tables` on the Repository object.
    - `show_changes` provides a dry-run of exactly what will occur, step by step.
    ```python
    >>> nd_repo.show_changes()
    1. Will DELETE Device: Device(id=123, site_xlink=...
    2. Will DELETE Device: Device(id=9000, site_xlink=...
    ```
    - `show_changes_as_tables` provides an aggregated overview of what is going to happen.
    ```python
    >>> nd_repo.show_changes_as_tables(terse=True)
        
    ## Device Changes

    action    site_xlink    asset_id_xlink    monitorstatus_xlink  
    --------  ------------  ----------------  ---------------------
    DELETE    137           None              None                 
    DELETE    137           None              None                 
    ```
6. You just remembered -- your supervisor asked you to append "`DONE`" to the Site name to  once the devices are deleted! Lets make that change as well:
```python
>>> site.name = f'{site.name} DONE'
```
7. Re-use `show_changes_as_tables` to see all the proposed changes:
```python
>>> nd_repo.show_changes_as_tables(terse=True, select_cols=['name'])
## Device Changes

action    name           
--------  ---------------
DELETE    foo.uoregon.edu
DELETE    bar.uoregon.edu

## Site Changes

action    name            
--------  ----------------
UPDATE    [-Death Star-]+D
          eath Star DONE+
```
8. *If the changes all look good*, then go ahead and commit them using `save_changes`:
```python
>>> nd_repo.save_changes()
100%|████████████████████████████████████████| 3/3 [00:00<00:00,  9.26it/s]
```

> ℹ Tip: For exceptionally small screens, adjust `TERSE` settings via [API Environment Variables](./generated-env-var-docs.md). 
> 
> Example: You can use the following settings, to *print one line per entry truncated to 16 characters*:
> ```sh
> export NETDOT_CLI_TERSE=True
> export NETDOT_CLI_TERSE_COL_WIDTH=16
> export NETDOT_CLI_TERSE_MAX_CHARS=16
> ```

#### Example 6: Code Sample (copy-paste friendly)

```python
for device in devices:
    device.delete()
nd_repo.show_changes()
nd_repo.show_changes_as_tables(terse=True)
site.name = f'{site.name} DONE'
nd_repo.show_changes_as_tables(terse=True, select_cols=['name'])
# And save all changes using:
# nd_repo.save_changes()
```

### Example 7: Show All Changes

*Continuing from the prior example,* you can use `show_all_changes` to see a report of **all** actions (including completed and failed actions):
> `show_all_changes` includes each of:
> * completed tasks,
> * planned tasks, and
> * *If there was a failure:* the latest failed task.
```python
>>> nd_repo.show_all_changes()

Completed Actions:

1. Finished DELETE Device: Device(id=123, site_xlink=...
2. Finished DELETE Device: Device(id=9000, site_xlink=...
3. Finished UPDATE Site: Site(id=137, site_xlink=...

Remaining Actions:

None, yet...

```

#### Example 7: Code Sample (copy-paste friendly)

```python
nd_repo.show_all_changes()
```

### Example 8: Plan and Create a new Netdot Site
<a id='example-8-plan-and-create-a-new-netdot-site'></a> 

Imagine you want to add a new site in Netdot, with rooms and all. Let's create a 'Test Site,' with 3 rooms and 1 closet, like the following:

- Site: 'Test Site'
    - Floor: 'Test Floor'
        - Room: 'Test Room 1'
        - Room: 'Test Room 2'
            - Closet: 'Test Closet 1'
        - Room: 'Test Room 3'

Let's create all these objects!

1. First, within a dry run, we will propose the new site:
```python
>>> site =  nd_repo.create_new(netdot.Site(name='Test Site'))
Will CREATE Site: Site(id=None, name='Test Site', aliases=None, availab...
```
2. Then, using that returned `site` Python object, we will call `site.add_floor`:
```python
>>> floor = site.add_floor(netdot.Floor(level='Test Floor'))
Will CREATE Floor: Floor(id=None, info=None, level='Test Floor', site=S...
```
3. Next, using that returned `floor` Python object, we will call `floor.add_room`:
```python
>>> room1 = floor.add_room(netdot.Room(name='Test Room 1'))
Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='...
>>> room2 = floor.add_room(netdot.Room(name='Test Room 2'))
Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='...
>>> room3 = floor.add_room(netdot.Room(name='Test Room 3'))
Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='...
```
4. Finally, we can call `room.add_closet` on any of our `room[123]` objects.
```python
>>> closet = room3.add_closet(netdot.Closet(name='Test Closet 1'))
Will CREATE Closet: Closet(id=None, access_key_type=None, asbestos_tile...
```
5. Ensure that the proposed changes look good via `show_changes`:
```
>>> nd_repo.show_changes()
1. Will CREATE Site: Site(id=None, name='Test Site', aliases=None, availabi...
2. Will CREATE Floor: Floor(id=None, info=None, level='Test Floor', site=Si...
3. Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='T...
4. Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='T...
5. Will CREATE Room: Room(id=None, floor=Floor(id=None, info=None, level='T...
6. Will CREATE Closet: Closet(id=None, access_key_type=None, asbestos_tiles...
```
1. Uh oh! Upon reviewing you see that "Test Closet 1" is in "Test Room 3" -- it is supposed to be in Room 2! Update the room for the closet using basic assignment operator:
```python
closet.room = room2
```
1. To ensure the change has occurred, use the `show_as_tables(select_cols=['name', 'room'])` to make sure that the closet has the right room associated to it:
> ℹ Wanna see the full "Room" object in the "Closet Changes" table-output? Use the keyword argument `display_full_objects=True`.
>> Alternately, set up your [`NETDOT_CLI_DISPLAY_FULL_OBJECTS` environment variable](./generated-env-var-docs.md)
```python
>>> repository.show_changes_as_tables(select_cols=['name', 'room'])
## Closet Changes

action    name           room
--------  -------------  -------------------------------
CREATE    Test Closet 1  Room(id=None, name=Test Room 2)

... trimmed for brevity... 
```
8. Looks good! So, finally, save the changes to Netdot using `save_changes()`
```python
>>> nd_repo.save_changes()
100%|████████████████████████████████████████| 6/6 [00:00<00:00,  9.26it/s]
```

> ℹ The created objects will have their `id` attribute populated by Netdot during `save_changes`.

#### Example 8: Code Sample (copy-paste friendly)

```python
site =  nd_repo.create_new(netdot.Site(name='Test Site'))
floor = site.add_floor(netdot.Floor(level='Test Floor'))
room1 = floor.add_room(netdot.Room(name='Test Room 1'))
room2 = floor.add_room(netdot.Room(name='Test Room 2'))
room3 = floor.add_room(netdot.Room(name='Test Room 3'))
closet = room3.add_closet(netdot.Closet(name='Test Closet 1'))
nd_repo.show_changes()
nd_repo.save_changes()  # This is a totally non-destructive change -- let it rip!
# Cleanup
# site.delete()
# nd_repo.save_changes()
```

# Scripted Usage

Once you have a feel for the full [Python Netdot API](./generated-api-docs.md), you can get to writing some scripts or tools to make your daily work in Netdot automated and simple.

## Connecting in a Script (via Environment Variables): `netdot.Repository()`

For starters, we need to set up a `Repository` to interact with NetDot.
Environment variables can be a good method for providing credentials to your script, as suggested here:

> ℹ This pairs nicely with Continuous Integration! 
> It also works well enough for local development using [python-dotenv](https://pypi.org/project/python-dotenv/) or similar.

```python
import os
import netdot

nd_repo = netdot.Repository(
    netdot_url=os.getenv('NETDOT_URL'), 
    user=os.getenv('NETDOT_USERNAME'), 
    password=os.getenv('NETDOT_PASSWORD'),
    dry_run=True,
    auto_update=True,
    print_changes=False,
)
```

### Example 9: Get all Rooms fed by a Switch

Given some Netdot Switch (Device), you can easily determine which all Rooms it feeds. 

> Assumption: Your Netdot Cable Plant has to have its HorizontalCables well-documented.

1. Lookup the Switch by name.
```python
name = 'foobar-sw09.example.com'
devices = nd_repo.get_devices_where(name=name)
assert len(devices) == 1, f"Found 0/more-than-one one device with name '{name}': {devices}"
switch = devices[0]
```
2. Collect a "Set" containing all of the rooms.
> ℹ Python Tip: Python's `set()` is a handy data structure -- it will automatically ensure that we only collect 'distinct' rooms (duplicates will be ignored)
```python
rooms = set()
for interface in switch.load_interfaces():
    jack = interface.load_jack()
    if jack:
        rooms.add(jack.room)
```
3. Print a nice report back out for reviewing.
> ℹ Python Tip: Python's `sorted` and `filter` functions can 'remove empty strings' and sort output for you!
```python
print(f"Rooms fed by {switch.name}:")
print('\n'.join(sorted(filter(None, rooms))))
```

#### Example 9: Code Sample (copy-paste friendly)

```python
name = 'foobar-sw09.example.com'
devices = nd_repo.get_devices_where(name=name)
assert len(devices) == 1, f"Found 0/more-than-one one device with name '{name}': {devices}"
switch = devices[0]
rooms = set()
for interface in switch.load_interfaces():
    jack = interface.load_jack()
    if jack:
        rooms.add(jack.room)
print(f"Rooms fed by {switch.name}:")
print('\n'.join(sorted(filter(None, rooms))))
```

### Example 10: Get all Jacks fed by a Switch

*Continuing from the prior example,* let's assume you want to know which jacks are actually fed by the switch within each room. 

4. Collect a "Dictionary" that maps from 'Room' to 'List of HorizontalCables'.
> ℹ Python Tip: Python's `defaultdict()` is very similar to `dict()`, but it will call a 'default factory function' if a value is missing.
```python
from collections import defaultdict
rooms = defaultdict(list)
for interface in switch.load_interfaces():
    jack = interface.load_jack()
    if jack:
        rooms[jack.room].append(jack)
```
5. Print a nice report back out for reviewing.
```python
for room, jacks in rooms.items():
    jack_list = '\n'.join([jack.jackid for jack in jacks])
    print(f'{room}\n{jack_list}\n')
```

#### Example 10: Code Sample (copy-paste friendly)

```python
# Get the Switch
name = 'foobar-sw09.example.com'
devices = nd_repo.get_devices_where(name=name)
assert len(devices) == 1, f"Found 0/more-than-one one device with name '{name}': {devices}"
switch = devices[0]

# Get all the Jacks
rooms = defaultdict(list)
for interface in switch.load_interfaces():
    jack = interface.load_jack()
    if jack:
        rooms[jack.room].append(jack)

# Print a report
for room, jacks in rooms.items():
    jack_list = '\n'.join([jack.jackid for jack in jacks])
    print(f'{room}\n{jack_list}\n')
```


### Example 11: Update 'aliases' of several Sites in NetDot

As a simple script example, imagine we want to update the 'aliases' with the string "` (odd layout)`" for some set of sites in NetDot.
In this example, we will write a script to do just that.

1. Now, we are given a list of `SITE_IDS` to which we want to update the 'alias' with the string "(odd layout)".
```python
SITE_IDS = [98, 124, 512, 123, 111]
```
2. We can use Python list comprehensions to download the sites, and make the updates locally.
```python
sites = [ nd_repo.get_site(id) for id in SITE_IDS ]
updated_sites = [ site.aliases=f'{site.aliases} (odd layout)' for site in sites ]
```
3. Then, it is time to apply the updates locally to the repository's "proposed changes"
```python
for updated_site in updated_sites:
    updated_site.update()
```
4. [Optionally] Add a step in your script to review all the proposed changes using `show_changes`
```python
nd_repo.show_changes()
```
5. Finally, save the changes back to Netdot using `save_changes`.
```python
nd_repo.save_changes()
```

#### Example 11: Code Sample (copy-paste friendly)

```python
# Get all the sites
SITE_IDS = [98, 124, 512, 123, 111]
sites = [ nd_repo.get_site(id) for id in SITE_IDS ]

# Update the sites
for site in sites:
    site.aliases=f'{site.aliases} (odd layout)'

# Save changes to Netdot
nd_repo.save_changes()
```

# Advanced Usage

Some features in this Netdot Python package are not key to normal use.
Those features are documented here.

## Proposed Changes Pickle File
<a id="proposed-changes-pickle-file"> </a>

If you have been working with a Netdot Repository in dry run mode, you might want to *save a snapshot of proposed changes, or a record of completed changes*.
This can be done with `save_as_pickle()`.

> ℹ By default, the file is saved with a version marker and timestamp -- this helps ensure future recoverability of the file's contents.

```python
nd_repo.proposed_changes.save_as_pickle()
'netdot-cli-0.4.0-proposed_changes-2023-11-08_14-51.pickle'
```

### Recovering Proposed Changes from Pickle File

> ℹ By default, a [Proposed Changes Pickle File](#proposed-changes-pickle-file) will be created in your current working directory *if **any exception** occurs during `save_changes()`.*

If an error occurs when you call `nd_repo.save_changes()`, you will likely want to be able to look at which actions completed and which did not.
When you have a pickle file, there are two routes forward for recovering these changes: Online (connected to Netdot), or Offline.


#### Online Recovery

To recover while connected to Netdot, load the pickle file directly into `nd_repo.proposed_changes` then continue using the `nd_repo` like normal: 

```python
nd_repo = netdot.connect()

# 1. Load the changes
nd_repo.proposed_changes = netdot.load('netdot-cli-0.4.0-proposed_changes-2023-11-08_14-51.pickle')

# 2. Review completed, planned, and failed actions:
nd_repo.show_all_changes()      # As a verbose report
nd_repo.show_failed_changes()   # Only showing failures
nd_repo.show_changes()          # Only showing planned actions
nd_repo.show_changes_as_tables(select_cols=['name', 'address'])

# 3. If planned action look good, try to call `save_changes` (again) to complete those remaining planned actions
nd_repo.save_changes()
```

#### Offline Recovery

If you would rather work with the file offline, the `netdot.UnitOfWork` does expose all of the same information (with slightly more access to the underlying Python objects):

```python
# 1. Load the changes
proposed_changes = netdot.load('netdot-cli-0.4.0-proposed_changes-2023-11-08_14-51.pickle')
# 2. Review them as Human Readable Reports
proposed_changes.status_report()
proposed_changes.failed_actions_msgs()
proposed_changes.dry_run()
# 3. Review them as Lists of Python objects
proposed_changes.failed_actions()
proposed_changes.as_list()
proposed_changes.completed_as_list()
```

## Multithreading for Parallelizing HTTP GET Requests

The `netdot.Repository` class can multithread *certain* HTTP requests.

To enable this, set the `NETDOT_CLI_THREADS` Environment Variable before running your python code.

```bash
export NETDOT_CLI_THREADS=4
```

You can override this number by passing the `threads` keyword argument to the Repository constructor.

```python
>>> repo = netdot.Repository(..., threads=4)
```

> This `threads` keyword argument can be used in the [interactive interface (discussed above)](#connecting-in-the-interpreter-netdotconnect) as well.
> ```python
> >>> repo = netdot.connect(threads=4)
> ```

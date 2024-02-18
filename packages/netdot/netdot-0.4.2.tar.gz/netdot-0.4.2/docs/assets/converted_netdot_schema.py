"""Python code representing NetDot Data Classes.

This was created by doing 'find and replace' in VSCode based on netdot_schemal.sql (a schema-dump of UO's NetDot).
"""

import ipaddress

import netdot.parse as parse


class accessright:
    access: str = None
    id: int = None
    object_class: str = None
    object_id: int = None


class asn:

    description: str = None
    id: int = None

    info: str = None
    number: int = None
    rir: str = None


class audit:

    fields: str = None
    id: int = None

    label: str = None
    object_id: int = None
    operation: str = None
    tablename: str = None
    tstamp: parse.DateTime = None
    username: str = None
    vals: str = None


class availability:

    id: int = None

    info: str = None
    name: str = None


class cabletype:

    id: int = None

    info: str = None
    name: str = None


class circuitstatus:

    id: int = None

    info: str = None
    name: str = None


class circuittype:

    id: int = None

    info: str = None
    name: str = None


class contactlist:

    id: int = None

    info: str = None
    name: str = None


class contacttype:

    id: int = None

    info: str = None
    name: str = None


class datacache:

    data: str = None
    id: int = None

    name: str = None
    tstamp: int = None


class deviceattrname:

    id: int = None

    info: str = None
    name: str = None


class dhcpattrname:

    code: int = None
    format: str = None
    id: int = None

    info: str = None
    name: str = None


class dhcpscopetype:

    id: int = None

    info: str = None
    name: str = None


class entity:

    acctnumber: str = None
    aliases: str = None
    asname: str = None
    asnumber: int = None
    availability: int = None
    contactlist: int = None
    id: int = None

    info: str = None
    maint_contract: str = None
    name: str = None
    oid: str = None
    short_name: str = None
    config_type: str = None


class entitytype:

    id: int = None

    info: str = None
    name: str = None


class entityrole:

    entity: int = None
    id: int = None

    type: int = None


class fibertype:

    id: int = None

    info: str = None
    name: str = None




class groupright:

    accessright: int = None
    contactlist: int = None
    id: int = None


class hostaudit:

    id: int = None

    tstamp: parse.DateTime = None
    zone: str = None
    scope: str = None
    pending: bool = False


class ipblockattrname:

    id: int = None

    info: str = None
    name: str = None


class ipblockstatus:

    id: int = None

    name: str = None


class maintcontract:

    id: int = None

    info: str = None
    number: str = None
    provider: int = None


class monitorstatus:

    id: int = None

    info: str = None
    name: str = None


class oui:

    id: int = None

    oui: str = None
    vendor: str = None



class producttype:

    id: int = None

    info: str = None
    name: str = None


class product:

    description: str = None
    id: int = None
    info: str = None
    manufacturer: int = None
    name: str = None
    sysobjectid: str = None
    type: int = None
    latest_os: str = None
    part_number: str = None
    config_type: str = None


class savedqueries:

    id: int = None

    name: str = None
    querytext: str = None


class schemainfo:

    id: int = None

    info: str = None
    version: str = None


class service:

    id: int = None

    info: str = None
    name: str = None


class site:

    aliases: str = None
    availability: int = None
    city: str = None
    contactlist: int = None
    country: str = None
    id: int = None

    info: str = None
    name: str = None
    number: str = None
    pobox: str = None
    state: str = None
    street1: str = None
    street2: str = None
    zip: str = None
    gsf: int = None


class entitysite:

    entity: int = None
    id: int = None

    site: int = None


class floor:

    id: int = None

    info: str = None
    level: str = None
    site: int = None


class floorpicture:

    bindata: str = None
    filename: str = None
    filesize: str = None
    filetype: str = None
    floor: int = None
    id: int = None

    info: str = None


class room:

    floor: int = None
    id: int = None

    name: str = None


class closet:

    access_key_type: str = None
    asbestos_tiles: bool = False
    catv_taps: str = None
    converted_patch_panels: bool = False
    dimensions: str = None
    ground_buss: bool = False
    hvac_type: str = None
    id: int = None

    info: str = None
    name: str = None
    room: int = None
    ot_blocks: str = None
    outlets: str = None
    pair_count: str = None
    patch_panels: str = None
    rack_type: str = None
    racks: str = None
    ru_avail: str = None
    shared_with: str = None
    ss_blocks: str = None
    work_needed: str = None


class backbonecable:

    end_closet: int = None
    id: int = None

    info: str = None
    installdate: parse.DateTime = None
    length: str = None
    name: str = None
    owner: int = None
    start_closet: int = None
    type: int = None


class closetpicture:

    bindata: str = None
    closet: int = None
    filename: str = None
    filesize: str = None
    filetype: str = None
    id: int = None

    info: str = None





class horizontalcable:

    account: str = None
    closet: int = None
    contactlist: int = None
    datetested: parse.DateTime = None
    faceplateid: str = None
    id: int = None

    info: str = None
    installdate: parse.DateTime = None
    jackid: str = None
    length: str = None
    room: int = None
    testpassed: bool = False
    type: int = None


class sitelink:

    entity: int = None
    farend: int = None
    id: int = None

    info: str = None
    name: str = None
    nearend: int = None


class circuit:

    cid: str = None
    id: int = None

    info: str = None
    installdate: parse.DateTime = None
    linkid: int = None
    speed: str = None
    status: int = None
    type: int = None
    vendor: int = None
    datetested: parse.DateTime = None
    loss: str = None


class sitepicture:

    bindata: str = None
    filename: str = None
    filesize: str = None
    filetype: str = None
    id: int = None

    info: str = None
    site: int = None


class strandstatus:

    id: int = None

    info: str = None
    name: str = None


class cablestrand:

    cable: int = None
    circuit_id: int = None
    description: str = None
    fiber_type: int = None
    id: int = None

    info: str = None
    name: str = None
    number: int = None
    status: int = None


class splice:

    id: int = None

    info: str = None
    strand1: int = None
    strand2: int = None


class usertype:
    id: int = None
    info: str = None
    name: str = None


class person:
    aliases: str = None
    cell: str = None
    email: str = None
    emailpager: str = None
    entity: int = None
    extension: int = None
    fax: str = None
    firstname: str = None
    home: str = None
    id: int = None
    info: str = None
    lastname: str = None
    location: int = None
    office: str = None
    pager: str = None
    position: str = None
    room: int = None
    user_type: int = None
    username: str = None
    password: str = None


class contact:
    contactlist: int = None
    contacttype: int = None
    escalation_level: int = None
    id: int = None
    info: str = None
    notify_email: int = None
    notify_pager: int = None
    notify_voice: int = None
    person: int = None


class userright:
    accessright: int = None
    id: int = None
    person: int = None


class vlangroup:
    description: str = None
    end_vid: int = None
    id: int = None
    info: str = None
    name: str = None
    start_vid: int = None


class vlan:
    description: str = None
    id: int = None
    info: str = None
    name: str = None
    vid: int = None
    vlangroup: str = None


class zone:
    active: bool = False
    contactlist: int = None
    expire: int = None
    id: int = None
    info: str = None
    minimum: int = None
    name: str = None
    refresh: int = None
    retry: int = None
    rname: str = None
    serial: int = None
    default_ttl: int = None
    export_file: str = None
    mname: str = None
    include: str = None


class rr:
    active: bool = False
    auto_update: bool = False
    expiration: parse.DateTime = None
    id: int = None
    info: str = None
    name: str = None
    zone: int = None
    created: parse.DateTime = None
    modified: parse.DateTime = None



class bgppeering:
    bgppeeraddr: str = None
    bgppeerid: str = None
    device: int = None
    entity: int = None
    id: int = None
    monitored: bool = False
    authkey: str = None
    info: str = None
    max_v4_prefixes: int = None
    max_v6_prefixes: int = None
    contactlist: int = None
    last_changed: parse.DateTime = None
    peer_group: str = None
    state: str = None


class deviceattr:
    device: int = None
    id: int = None
    name: int = None
    value: str = None


class devicecontacts:
    contactlist: int = None
    device: int = None
    id: int = None


class devicemodule:
    clazz: str = None
    contained_in: int = None
    date_installed: parse.DateTime = None
    description: str = None
    device: int = None
    fru: bool = False
    fw_rev: str = None
    hw_rev: str = None
    id: int = None
    last_updated: parse.DateTime = None
    model: str = None
    name: str = None
    number: int = None
    pos: int = None
    sw_rev: str = None
    type: str = None
    asset_id: int = None


class ipblock:

    address: ipaddress.ip_address
    description: str = None
    first_seen: parse.DateTime = None
    id: int = None

    info: str = None
    interface: int = None
    last_seen: parse.DateTime = None
    owner: int = None
    parent: int = None
    prefix: int = None
    status: int = None
    used_by: int = None
    version: int = None
    vlan: int = None
    use_network_broadcast: bool = False
    monitored: bool = False
    rir: str = None
    asn: int = None




class dhcpscope:

    ipblock: int = None
    id: int = None

    text: str = None
    name: str = None
    container: int = None
    physaddr: int = None
    type: int = None
    export_file: str = None
    enable_failover: bool = False
    failover_peer: str = None
    active: bool = False
    duid: str = None
    version: int = None


class dhcpattr:

    id: int = None

    name: int = None
    scope: int = None
    value: str = None


class dhcpscopeuse:

    id: int = None

    scope: int = None
    template: int = None


class ipblockattr:

    id: int = None

    ipblock: int = None
    name: int = None
    value: str = None


class ipservice:

    contactlist: int = None
    id: int = None

    ip: int = None
    monitored: bool = False
    monitorstatus: int = None
    service: int = None


class rraddr:

    id: int = None

    ipblock: int = None
    rr: int = None
    ttl: str = None


class rrcname:

    cname: str = None
    rr: int = None
    id: int = None

    ttl: str = None


class rrds:

    algorithm: int = None
    digest: str = None
    digest_type: int = None
    id: int = None

    key_tag: int = None
    rr: int = None
    ttl: str = None


class rrhinfo:

    cpu: str = None
    id: int = None

    os: str = None
    rr: int = None
    ttl: str = None


class rrloc:

    altitude: int = None
    horiz_pre: str = None
    id: int = None

    latitude: str = None
    longitude: str = None
    rr: int = None
    size: str = None
    ttl: str = None
    vert_pre: str = None


class rrmx:

    exchange: str = None
    id: int = None

    preference: int = None
    rr: int = None
    ttl: str = None


class rrnaptr:

    flags: str = None
    id: int = None

    order_field: int = None
    preference: int = None
    regexpr: str = None
    replacement: str = None
    rr: int = None
    services: str = None
    ttl: str = None


class rrns:

    id: int = None

    nsdname: str = None
    rr: int = None
    ttl: str = None


class rrptr:

    id: int = None

    ipblock: int = None
    rr: int = None
    ttl: str = None
    ptrdname: str = None


class rrsrv:

    id: int = None

    port: int = None
    priority: int = None
    rr: int = None
    target: str = None
    ttl: str = None
    weight: int = None


class rrtxt:

    id: int = None

    rr: int = None
    ttl: str = None
    txtdata: str = None


class sitesubnet:

    id: int = None

    site: int = None
    subnet: int = None


class stpinstance:
    bridge_priority: int = None
    device: int = None
    id: int = None
    number: int = None
    root_bridge: str = None
    root_port: int = None


class interfacevlan:

    id: int = None
    interface: int = None
    stp_des_bridge: str = None
    stp_des_port: str = None
    stp_instance: int = None
    stp_state: str = None
    vlan: int = None


class subnetzone:

    id: int = None

    subnet: int = None
    zone: int = None


class zonealias:

    id: int = None

    info: str = None
    name: str = None
    zone: int = None

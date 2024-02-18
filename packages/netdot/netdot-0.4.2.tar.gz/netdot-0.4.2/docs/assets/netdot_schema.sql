create table accessright
(
    access: str = None
    id: int = None
        
    object_class: str = None
    object_id: int = None
);

create table asn
(
    description: str = None
    id: int = None
        
    info        text         null,
    number: int = None
    rir: str = None
    constraint asn1
        unique (number)
);

create index ASN2
    on asn (rir);

create table audit
(
    fields: str = None
    id: int = None
        
    label: str = None
    object_id: int = None
    operation: str = None
    tablename: str = None
    tstamp    timestamp default '1970-01-02 00:00:01' not null,
    username: str = None
    vals: str = None
);

create index Audit2
    on audit (tstamp);

create index Audit3
    on audit (username);

create index Audit4
    on audit (tablename);

create index Audit5
    on audit (label);

create table availability
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint availability1
        unique (name)
);

create table cabletype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint cabletype1
        unique (name)
);

create table circuitstatus
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint circuitstatus1
        unique (name)
);

create table circuittype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint circuittype1
        unique (name)
);

create table contactlist
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint contactlist1
        unique (name)
);

create table contacttype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint contacttype1
        unique (name)
);

create table datacache
(
    data   longblob         null,
    id: int = None
        
    name: str = None
    tstamp: int = None
    constraint datacache1
        unique (name)
);

create table deviceattrname
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint deviceattrname1
        unique (name)
);

create table dhcpattrname
(
    code: int = None
    format: str = None
    id: int = None
        
    info: str = None
    name: str = None
    constraint dhcpattrname1
        unique (name)
);

create table dhcpscopetype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint dhcpscopetype1
        unique (name)
);

create table entity
(
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
    constraint entity1
        unique (name),
    constraint entity2
        unique (oid),
    constraint fk_availability
        foreign key (availability) references availability (id),
    constraint fk_contactlist_2
        foreign key (contactlist) references contactlist (id)
);

create index Entity3
    on entity (asname);

create index Entity4
    on entity (asnumber);

create index availability
    on entity (availability);

create index contactlist
    on entity (contactlist);

create table entitytype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint entitytype1
        unique (name)
);

create table entityrole
(
    entity: int = None
    id: int = None
        
    type: int = None
    constraint entityrole1
        unique (entity, type),
    constraint fk_entity_1
        foreign key (entity) references entity (id),
    constraint fk_type_3
        foreign key (type) references entitytype (id)
);

create table fibertype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint fibertype1
        unique (name)
);

create index FiberType2
    on fibertype (name);

create table fwtable
(
    device: int = None
    id: int = None
        
    tstamp timestamp default '1970-01-02 08:00:01' not null,
    constraint fwtable1
        unique (device, tstamp)
);

create index FWTable2
    on fwtable (device);

create index FWTable3
    on fwtable (tstamp);

create table fwtableentry
(
    fwtable: int = None
    id: int = None
        
: int = None
    physaddr: int = None
);

create index FWTableEntry1
    on fwtableentry (fwtable);

create index FWTableEntry2
    on fwtableentry (interface);

create index FWTableEntry3
    on fwtableentry (physaddr);

create table groupright
(
    accessright: int = None
    contactlist: int = None
    id: int = None
        
    constraint groupright1
        unique (contactlist, accessright),
    constraint fk_accessright
        foreign key (accessright) references accessright (id),
    constraint fk_contactlist_3
        foreign key (contactlist) references contactlist (id)
);

create index GroupRight2
    on groupright (accessright);

create table hostaudit
(
    id: int = None
        
    tstamp  timestamp  default '1970-01-01 00:00:01' not null,
    zone: str = None
    scope: str = None
    pending : bool = False                     not null
);

create index HostAudit2
    on hostaudit (zone);

create index HostAudit3
    on hostaudit (scope);

create index HostAudit6
    on hostaudit (pending);

create table ipblockattrname
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint ipblockattrname1
        unique (name)
);

create table ipblockstatus
(
    id: int = None
        
    name: str = None
    constraint ipblockstatus1
        unique (name)
);

create table maintcontract
(
    id: int = None
        
    info: str = None
    number: str = None
    provider: int = None
    constraint maintcontract1
        unique (number),
    constraint fk_provider
        foreign key (provider) references entity (id)
);

create index provider
    on maintcontract (provider);

create table monitorstatus
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint monitorstatus1
        unique (name)
);

create table oui
(
    id: int = None
        
    oui: str = None
    vendor: str = None
    constraint oui1
        unique (oui)
);

create table physaddr
(
    address: str = None
    first_seen timestamp  default '1970-01-01 00:00:00' not null,
    id: int = None
        
    last_seen  timestamp  default '1970-01-01 00:00:01' not null,
    static     : bool = False                     not null,
    constraint physaddr1
        unique (address)
);

create index PhysAddr2
    on physaddr (first_seen);

create index PhysAddr3
    on physaddr (last_seen);

create table physaddrattrname
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint physaddrattrname1
        unique (name)
);

create table physaddrattr
(
    id: int = None
        
    name: int = None
    physaddr: int = None
    value: str = None
    constraint physaddrattr1
        unique (name, physaddr),
    constraint fk_name_4
        foreign key (name) references physaddrattrname (id),
    constraint fk_physaddr_5
        foreign key (physaddr) references physaddr (id)
);

create index PhysAddrAttr2
    on physaddrattr (physaddr);

create table producttype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint producttype1
        unique (name)
);

create table product
(
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
    constraint product1
        unique (name, manufacturer),
    constraint fk_manufacturer
        foreign key (manufacturer) references entity (id),
    constraint fk_type_5
        foreign key (type) references producttype (id)
);

create table asset
(
    custom_serial: str = None
    updated: netdot_sites_manager.parse.DateTime = None
    description: str = None
    id: int = None
    info: str = None
    inventory_number: str = None
    maint_contract: str = None
    maint_contract_xlink: int = None
    maint_from: netdot_sites_manager.parse.DateTime = None
    maint_until: netdot_sites_manager.parse.DateTime = None
    physaddr: int = None
    po_number: str = None
    product_id: int = None
    reserved_for: str = None
    serial_number: str = None
    constraint fk_physaddr_1
        foreign key (physaddr) references physaddr (id),
    constraint fk_product_id
        foreign key (product_id) references product (id)
);

create index Asset3
    on asset (serial_number);

create index Asset4
    on asset (inventory_number);

create index Asset5
    on asset (po_number);

create index maint_contract
    on asset (maint_contract);

create index Product2
    on product (sysobjectid);

create index Product3
    on product (type);

create index latest_os
    on product (latest_os);

create table savedqueries
(
    id: int = None
        
    name: str = None
    querytext text         not null,
    constraint savedqueries1
        unique (name)
);

create table schemainfo
(
    id: int = None
        
    info: str = None
    version: str = None
    constraint schemainfo1
        unique (version)
);

create table service
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint service1
        unique (name)
);

create table site
(
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
    constraint Site5
        unique (number),
    constraint site1
        unique (name),
    constraint fk_availability_1
        foreign key (availability) references availability (id),
    constraint fk_contactlist_7
        foreign key (contactlist) references contactlist (id)
);

create table entitysite
(
    entity: int = None
    id: int = None
        
    site: int = None
    constraint entitysite1
        unique (entity, site),
    constraint fk_entity_2
        foreign key (entity) references entity (id),
    constraint fk_site_1
        foreign key (site) references site (id)
);

create table floor
(
    id: int = None
        
    info: str = None
    level: str = None
    site: int = None
    constraint floor1
        unique (level, site),
    constraint fk_site_2
        foreign key (site) references site (id)
);

create table floorpicture
(
    bindata  longblob    not null,
    filename: str = None
    filesize: str = None
    filetype: str = None
    floor: int = None
    id: int = None
        
    info: str = None
    constraint floorpicture1
        unique (filename, floor),
    constraint fk_floor
        foreign key (floor) references floor (id)
);

create table room
(
    floor: int = None
    id: int = None
        
    name: str = None
    constraint room1
        unique (name, floor),
    constraint fk_floor_1
        foreign key (floor) references floor (id)
);

create table closet
(
    access_key_type: str = None
    asbestos_tiles         : bool = False not null,
    catv_taps: str = None
    converted_patch_panels : bool = False not null,
    dimensions: str = None
    ground_buss            : bool = False not null,
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
    constraint Closet1
        unique (name, room),
    constraint fk_room
        foreign key (room) references room (id)
);

create table backbonecable
(
    end_closet: int = None
    id: int = None
        
    info: str = None
    installdate: netdot_sites_manager.parse.DateTime = None
    length: str = None
    name: str = None
    owner: int = None
    start_closet: int = None
    type: int = None
    constraint backbonecable1
        unique (name),
    constraint fk_end_closet
        foreign key (end_closet) references closet (id),
    constraint fk_owner
        foreign key (owner) references entity (id),
    constraint fk_start_closet
        foreign key (start_closet) references closet (id),
    constraint fk_type
        foreign key (type) references cabletype (id)
);

create index BackboneCable2
    on backbonecable (name);

create index BackboneCable3
    on backbonecable (start_closet);

create index BackboneCable4
    on backbonecable (end_closet);

create index owner
    on backbonecable (owner);

create index type
    on backbonecable (type);

create index Closet3
    on closet (room);

create table closetpicture
(
    bindata  longblob    not null,
    closet: int = None
    filename: str = None
    filesize: str = None
    filetype: str = None
    id: int = None
        
    info: str = None
    constraint closetpicture1
        unique (filename, closet),
    constraint fk_closet
        foreign key (closet) references closet (id)
);

create table horizontalcable
(
    account: str = None
    closet: int = None
    contactlist: int = None
: netdot_sites_manager.parse.DateTime = None
    faceplateid: str = None
    id: int = None
        
    info: str = None
    installdate: netdot_sites_manager.parse.DateTime = None
    jackid: str = None
    length: str = None
    room: int = None
    testpassed  : bool = False not null,
    type: int = None
    constraint horizontalcable1
        unique (jackid, faceplateid, closet, room),
    constraint fk_closet_1
        foreign key (closet) references closet (id),
    constraint fk_contactlist_4
        foreign key (contactlist) references contactlist (id),
    constraint fk_room_2
        foreign key (room) references room (id),
    constraint fk_type_4
        foreign key (type) references cabletype (id)
);

create index HorizontalCable2
    on horizontalcable (account);

create index contactlist
    on horizontalcable (contactlist);

create index type
    on horizontalcable (type);

create index Room2
    on room (name);

create index Room3
    on room (floor);

create index Site2
    on site (street1);

create index Site3
    on site (name);

create index Site4
    on site (number);

create index availability
    on site (availability);

create index contactlist
    on site (contactlist);

create table sitelink
(
    entity: int = None
    farend: int = None
    id: int = None
        
    info: str = None
    name: str = None
    nearend: int = None
    constraint sitelink1
        unique (name),
    constraint fk_entity_4
        foreign key (entity) references entity (id),
    constraint fk_farend
        foreign key (farend) references site (id),
    constraint fk_nearend
        foreign key (nearend) references site (id)
);

create table circuit
(
    cid: str = None
    id: int = None
        
    info: str = None
    installdate: netdot_sites_manager.parse.DateTime = None
    linkid: int = None
    speed: str = None
    status: int = None
    type: int = None
    vendor: int = None
: netdot_sites_manager.parse.DateTime = None
    loss: str = None
    constraint circuit1
        unique (vendor, cid),
    constraint fk_linkid
        foreign key (linkid) references sitelink (id),
    constraint fk_status_1
        foreign key (status) references circuitstatus (id),
    constraint fk_type_1
        foreign key (type) references circuittype (id),
    constraint fk_vendor
        foreign key (vendor) references entity (id)
);

create index Circuit2
    on circuit (linkid);

create index status
    on circuit (status);

create index type
    on circuit (type);

create index entity
    on sitelink (entity);

create index farend
    on sitelink (farend);

create index nearend
    on sitelink (nearend);

create table sitepicture
(
    bindata  longblob    not null,
    filename: str = None
    filesize: str = None
    filetype: str = None
    id: int = None
        
    info: str = None
    site: int = None
    constraint sitepicture1
        unique (filename, site),
    constraint fk_site_3
        foreign key (site) references site (id)
);

create table strandstatus
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint strandstatus1
        unique (name)
);

create table cablestrand
(
    cable: int = None
    circuit_id: int = None
    description: str = None
    fiber_type: int = None
    id: int = None
        
    info: str = None
    name: str = None
    number: int = None
    status: int = None
    constraint cablestrand1
        unique (cable, name),
    constraint fk_cable
        foreign key (cable) references backbonecable (id),
    constraint fk_circuit_id
        foreign key (circuit_id) references circuit (id),
    constraint fk_fiber_type
        foreign key (fiber_type) references fibertype (id),
    constraint fk_status
        foreign key (status) references strandstatus (id)
);

create index CableStrand2
    on cablestrand (cable);

create index CableStrand3
    on cablestrand (name);

create index CableStrand4
    on cablestrand (number);

create index CableStrand5
    on cablestrand (circuit_id);

create index fiber_type
    on cablestrand (fiber_type);

create index status
    on cablestrand (status);

create table splice
(
    id: int = None
        
    info: str = None
    strand1: int = None
    strand2: int = None
    constraint fk_strand1
        foreign key (strand1) references cablestrand (id),
    constraint fk_strand2
        foreign key (strand2) references cablestrand (id)
);

create index Splice1
    on splice (strand1);

create index Splice2
    on splice (strand2);

create table usertype
(
    id: int = None
        
    info: str = None
    name: str = None
    constraint usertype1
        unique (name)
);

create table person
(
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
    constraint Person3
        unique (email),
    constraint person1
        unique (firstname, lastname, entity),
    constraint person2
        unique (username),
    constraint fk_entity_3
        foreign key (entity) references entity (id),
    constraint fk_location
        foreign key (location) references site (id),
    constraint fk_room_3
        foreign key (room) references room (id),
    constraint fk_user_type
        foreign key (user_type) references usertype (id)
);

create table contact
(
    contactlist: int = None
    contacttype: int = None
    escalation_level int        not null,
    id: int = None
        
    info: str = None
    notify_email: int = None
    notify_pager: int = None
    notify_voice: int = None
    person: int = None
    constraint fk_contactlist
        foreign key (contactlist) references contactlist (id),
    constraint fk_contacttype
        foreign key (contacttype) references contacttype (id),
    constraint fk_notify_email
        foreign key (notify_email) references availability (id),
    constraint fk_notify_pager
        foreign key (notify_pager) references availability (id),
    constraint fk_notify_voice
        foreign key (notify_voice) references availability (id),
    constraint fk_person
        foreign key (person) references person (id)
);

create index Contact1
    on contact (contactlist);

create index Contact2
    on contact (contacttype);

create index notify_email
    on contact (notify_email);

create index notify_pager
    on contact (notify_pager);

create index notify_voice
    on contact (notify_voice);

create index person
    on contact (person);

create index location
    on person (location);

create index room
    on person (room);

create index user_type
    on person (user_type);

create table userright
(
    accessright: int = None
    id: int = None
        
    person: int = None
    constraint userright1
        unique (person, accessright),
    constraint fk_accessright_1
        foreign key (accessright) references accessright (id),
    constraint fk_person_1
        foreign key (person) references person (id)
);

create index UserRight2
    on userright (accessright);

create table vlangroup
(
    description: str = None
    end_vid: int = None
    id: int = None
        
    info: str = None
    name: str = None
    start_vid: int = None
    constraint vlangroup1
        unique (name)
);

create table vlan
(
    description: str = None
    id: int = None
    info: str = None
    name: str = None
    vid: int = None
    vlangroup: int = None
    constraint vlan1
        unique (vid),
    constraint fk_vlangroup
        foreign key (vlangroup) references vlangroup (id)
);

create index Vlan2
    on vlan (vlangroup);

create table zone
(
    active      : bool = False not null,
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
    default_ttl int                  not null,
    export_file: str = None
    mname: str = None
    include: str = None
    constraint zone1
        unique (name),
    constraint fk_contactlist_8
        foreign key (contactlist) references contactlist (id)
);

create table rr
(
    active      : bool = False                     not null,
    auto_update : bool = False                     not null,
    expiration: netdot_sites_manager.parse.DateTime = None
    id: int = None
        
    info: str = None
    name: str = None
    zone: int = None
    created     timestamp  default CURRENT_TIMESTAMP     not null on update CURRENT_TIMESTAMP,
    modified    timestamp  default '0000-00-00 00:00:00' not null,
    constraint rr1
        unique (zone, name),
    constraint fk_zone
        foreign key (zone) references zone (id)
);

create table device
(
    aliases: str = None
    bgpid: str = None
    bgplocalas: int = None
    canautoupdate        : bool = False                     not null,
    collect_arp          : bool = False                     not null,
    collect_fwt          : bool = False                     not null,
    collect_stp          : bool = False                     not null,
    community: str = None
    customer_managed     : bool = False                     not null,
: netdot_sites_manager.parse.DateTime = None
    down_from: netdot_sites_manager.parse.DateTime = None
    down_until: netdot_sites_manager.parse.DateTime = None
    id: int = None
        
    info: str = None
    ipforwarding         : bool = False                     not null,
    last_arp             timestamp  default '1970-01-01 00:00:00' not null,
    last_fwt             timestamp  default '1970-01-01 00:00:00' not null,
    last_updated         timestamp  default '1970-01-01 00:00:01' not null,
    layers: str = None
    monitor_config       : bool = False                     not null,
    monitor_config_group: str = None
    monitored            : bool = False                     not null,
    monitoring_path_cost int                                      null,
    monitorstatus: int = None
    name: int = None
    oobname: str = None
    oobnumber: str = None
    os: str = None
    owner: int = None
    rack: str = None
    room: int = None
    site: int = None
    snmp_authkey: str = None
    snmp_authprotocol: str = None
    snmp_bulk            : bool = False                     not null,
    snmp_managed         : bool = False                     not null,
    snmp_polling         : bool = False                     not null,
    snmp_privkey: str = None
    snmp_privprotocol: str = None
    snmp_securitylevel: str = None
    snmp_securityname: str = None
    snmp_target: int = None
    snmp_version: int = None
    stp_enabled          : bool = False                     not null,
    stp_mst_digest: str = None
    stp_mst_region: str = None
    stp_mst_rev: int = None
    stp_type: str = None
    sysdescription: str = None
    syslocation: str = None
    sysname: str = None
    used_by: int = None
    auto_dns             : bool = False                     not null,
    asset_id: int = None
    extension: int = None
    snmp_conn_attempts: int = None
    snmp_down            : bool = False                     not null,
    oobname_2: str = None
    oobnumber_2: str = None
    power_outlet: str = None
    power_outlet_2: str = None
    monitoring_template: str = None
    host_device: int = None
    constraint device1
        unique (name, asset_id),
    constraint device2
        unique (name),
    constraint fk_asset_id
        foreign key (asset_id) references asset (id),
    constraint fk_bgplocalas
        foreign key (bgplocalas) references asn (id),
    constraint fk_host_device
        foreign key (host_device) references device (id),
    constraint fk_monitorstatus_1
        foreign key (monitorstatus) references monitorstatus (id),
    constraint fk_name
        foreign key (name) references rr (id),
    constraint fk_owner_1
        foreign key (owner) references entity (id),
    constraint fk_room_1
        foreign key (room) references room (id),
    constraint fk_site
        foreign key (site) references site (id),
    constraint fk_used_by
        foreign key (used_by) references entity (id)
);

create table arpcache
(
    device: int = None
    id: int = None
        
    tstamp timestamp default '1970-01-02 00:00:01' not null,
    constraint arpcache1
        unique (device, tstamp),
    constraint fk_device
        foreign key (device) references device (id)
);

create index ArpCache2
    on arpcache (device);

create index ArpCache3
    on arpcache (tstamp);

create table bgppeering
(
    bgppeeraddr: str = None
    bgppeerid: str = None
    device: int = None
    entity: int = None
    id: int = None
        
    monitored       : bool = False                 not null,
    authkey: str = None
    info: str = None
    max_v4_prefixes int                                  not null,
    max_v6_prefixes int                                  not null,
    contactlist: int = None
    last_changed    timestamp  default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    peer_group: str = None
    state: str = None
    constraint bgppeering1
        unique (device, bgppeeraddr),
    constraint fk_contactlist_bgppeering
        foreign key (contactlist) references contactlist (id),
    constraint fk_device_1
        foreign key (device) references device (id),
    constraint fk_entity
        foreign key (entity) references entity (id)
);

create index BGPPeering2
    on bgppeering (bgppeerid);

create index contactlist
    on bgppeering (contactlist);

create index Device3
    on device (used_by);

create index Device4
    on device (owner);

create index Device5
    on device (os);

create index Device6
    on device (sysname);

create index Device7
    on device (down_from);

create index Device8
    on device (down_until);

create index Device9
    on device (extension);

create index bgplocalas
    on device (bgplocalas);

create index host_device
    on device (host_device);

create index monitorstatus
    on device (monitorstatus);

create index room
    on device (room);

create index site
    on device (site);

create index snmp_target
    on device (snmp_target);

create table deviceattr
(
    device: int = None
    id: int = None
        
    name: int = None
    value: str = None
    constraint deviceattr1
        unique (name, device),
    constraint fk_device_2
        foreign key (device) references device (id),
    constraint fk_name_1
        foreign key (name) references deviceattrname (id)
);

create index DeviceAttr2
    on deviceattr (device);

create table devicecontacts
(
    contactlist: int = None
    device: int = None
    id: int = None
        
    constraint devicecontacts1
        unique (device, contactlist),
    constraint fk_contactlist_1
        foreign key (contactlist) references contactlist (id),
    constraint fk_device_3
        foreign key (device) references device (id)
);

create table devicemodule
(
    class: str = None
    contained_in: int = None
: netdot_sites_manager.parse.DateTime = None
    description: str = None
    device: int = None
    fru            : bool = False                     not null,
    fw_rev: str = None
    hw_rev: str = None
    id: int = None
        
    last_updated   timestamp  default '1970-01-01 00:00:01' not null,
    model: str = None
    name: str = None
    number: int = None
    pos: int = None
    sw_rev: str = None
    type: str = None
    asset_id: int = None
    constraint devicemodule1
        unique (device, number),
    constraint fk_asset_id_1
        foreign key (asset_id) references asset (id),
    constraint fk_device_4
        foreign key (device) references device (id)
);

create index asset_id
    on devicemodule (asset_id);

create table interface
(
    admin_duplex: str = None
    admin_status: str = None
    bpdu_filter_enabled : bool = False not null,
    bpdu_guard_enabled  : bool = False not null,
    contactlist: int = None
    description: str = None
    device: int = None
    doc_status: str = None
    down_from: netdot_sites_manager.parse.DateTime = None
    down_until: netdot_sites_manager.parse.DateTime = None
    dp_remote_id: str = None
    dp_remote_ip: str = None
    dp_remote_port: str = None
    dp_remote_type: str = None
    id: int = None
        
    info: str = None
    jack: int = None
    jack_char: str = None
    loop_guard_enabled  : bool = False not null,
    monitored           : bool = False not null,
    monitorstatus: int = None
    name: str = None
    neighbor: int = None
    neighbor_fixed      : bool = False not null,
    neighbor_missed: int = None
    number: str = None
    oper_duplex: str = None
    oper_status: str = None
    overwrite_descr     : bool = False not null,
    physaddr: int = None
    room_char: str = None
    root_guard_enabled  : bool = False not null,
    snmp_managed        : bool = False not null,
    speed: int = None
    stp_id: str = None
    type: str = None
    ignore_ip           : bool = False not null,
    auto_dns            : bool = False not null,
    circuit: int = None
    dlci: str = None
    constraint interface1
        unique (device, number, name),
    constraint fk_circuit
        foreign key (circuit) references circuit (id),
    constraint fk_contactlist_5
        foreign key (contactlist) references contactlist (id),
    constraint fk_device_6
        foreign key (device) references device (id),
    constraint fk_jack
        foreign key (jack) references horizontalcable (id),
    constraint fk_monitorstatus_2
        foreign key (monitorstatus) references monitorstatus (id),
    constraint fk_neighbor
        foreign key (neighbor) references interface (id),
    constraint fk_physaddr_4
        foreign key (physaddr) references physaddr (id)
);

create index Interface10
    on interface (circuit);

create index Interface2
    on interface (description);

create index Interface3
    on interface (stp_id);

create index Interface4
    on interface (physaddr);

create index Interface5
    on interface (jack);

create index Interface6
    on interface (neighbor);

create index Interface7
    on interface (oper_duplex);

create index Interface8
    on interface (oper_status);

create index Interface9
    on interface (speed);

create index contactlist
    on interface (contactlist);

create index monitorstatus
    on interface (monitorstatus);

create table ipblock
(
    address               decimal(40)                              not null,
    description: str = None
    first_seen            timestamp  default '1970-01-01 00:00:00' not null,
    id: int = None
        
    info: str = None
: int = None
    last_seen             timestamp  default '1970-01-01 00:00:01' not null,
    owner: int = None
    parent: int = None
    prefix: int = None
    status: int = None
    used_by: int = None
    version: int = None
    vlan: int = None
    use_network_broadcast : bool = False                     not null,
    monitored             : bool = False                     not null,
    rir: str = None
    asn: int = None
    constraint ipblock1
        unique (address, prefix),
    constraint fk_asn
        foreign key (asn) references asn (id),
    constraint fk_interface_3
        foreign key (interface) references interface (id),
    constraint fk_owner_2
        foreign key (owner) references entity (id),
    constraint fk_parent
        foreign key (parent) references ipblock (id),
    constraint fk_status_2
        foreign key (status) references ipblockstatus (id),
    constraint fk_used_by_1
        foreign key (used_by) references entity (id),
    constraint fk_vlan_1
        foreign key (vlan) references vlan (id)
);

create table arpcacheentry
(
    arpcache: int = None
    id: int = None
        
: int = None
    ipaddr: int = None
    physaddr: int = None
    constraint fk_arpcache
        foreign key (arpcache) references arpcache (id),
    constraint fk_interface
        foreign key (interface) references interface (id),
    constraint fk_ipaddr
        foreign key (ipaddr) references ipblock (id),
    constraint fk_physaddr
        foreign key (physaddr) references physaddr (id)
);

create index ArpCacheEntry1
    on arpcacheentry (arpcache);

create index ArpCacheEntry2
    on arpcacheentry (interface);

create index ArpCacheEntry3
    on arpcacheentry (physaddr);

create index ArpCacheEntry4
    on arpcacheentry (ipaddr);

alter table device
    add constraint fk_snmp_target
        foreign key (snmp_target) references ipblock (id);

create table dhcpscope
(
    ipblock: int = None
    id: int = None
        
    text: str = None
    name: str = None
    container: int = None
    physaddr: int = None
    type: int = None
    export_file: str = None
    enable_failover : bool = False not null,
    failover_peer: str = None
    active          : bool = False not null,
    duid: str = None
    version: int = None
    constraint dhcpscope1
        unique (name),
    constraint fk_container
        foreign key (container) references dhcpscope (id),
    constraint fk_ipblock
        foreign key (ipblock) references ipblock (id),
    constraint fk_physaddr_2
        foreign key (physaddr) references physaddr (id),
    constraint fk_type_2
        foreign key (type) references dhcpscopetype (id)
);

create table dhcpattr
(
    id: int = None
        
    name: int = None
    scope: int = None
    value: str = None
    constraint fk_name_2
        foreign key (name) references dhcpattrname (id),
    constraint fk_scope
        foreign key (scope) references dhcpscope (id)
);

create index DhcpAttr2
    on dhcpattr (scope);

create index dhcpattr1
    on dhcpattr (name, scope);

create index DhcpScope2
    on dhcpscope (ipblock);

create index DhcpScope3
    on dhcpscope (type);

create index DhcpScope4
    on dhcpscope (physaddr);

create index container
    on dhcpscope (container);

create table dhcpscopeuse
(
    id: int = None
        
    scope: int = None
    template: int = None
    constraint dhcpscopeuse1
        unique (scope, template),
    constraint fk_scope_1
        foreign key (scope) references dhcpscope (id),
    constraint fk_template
        foreign key (template) references dhcpscope (id)
);

create index DhcpScopeUse2
    on dhcpscopeuse (template);

create index Ipblock2
    on ipblock (parent);

create index Ipblock3
    on ipblock (status);

create index Ipblock4
    on ipblock (first_seen);

create index Ipblock5
    on ipblock (last_seen);

create index Ipblock6
    on ipblock (interface);

create index Ipblock7
    on ipblock (vlan);

create index asn
    on ipblock (asn);

create index ipblock8
    on ipblock (version);

create index owner
    on ipblock (owner);

create index used_by
    on ipblock (used_by);

create table ipblockattr
(
    id: int = None
        
    ipblock: int = None
    name: int = None
    value: str = None
    constraint ipblockattr1
        unique (name, ipblock),
    constraint fk_ipblock_1
        foreign key (ipblock) references ipblock (id),
    constraint fk_name_3
        foreign key (name) references ipblockattrname (id)
);

create index IpblockAttr2
    on ipblockattr (ipblock);

create table ipservice
(
    contactlist: int = None
    id: int = None
        
    ip: int = None
    monitored     : bool = False not null,
    monitorstatus: int = None
    service: int = None
    constraint ipservice1
        unique (ip, service),
    constraint fk_contactlist_6
        foreign key (contactlist) references contactlist (id),
    constraint fk_ip
        foreign key (ip) references ipblock (id),
    constraint fk_monitorstatus_3
        foreign key (monitorstatus) references monitorstatus (id),
    constraint fk_service
        foreign key (service) references service (id)
);

create index contactlist
    on ipservice (contactlist);

create index monitorstatus
    on ipservice (monitorstatus);

create index RR2
    on rr (name);

create index RR3
    on rr (expiration);

create index RR4
    on rr (created);

create index RR5
    on rr (modified);

create table rraddr
(
    id: int = None
        
    ipblock: int = None
    rr: int = None
    ttl: str = None
    constraint rraddr1
        unique (rr, ipblock),
    constraint fk_ipblock_2
        foreign key (ipblock) references ipblock (id),
    constraint fk_rr
        foreign key (rr) references rr (id)
);

create index RRADDR2
    on rraddr (ipblock);

create table rrcname
(
    cname: str = None
    rr: int = None
    id: int = None
        
    ttl: str = None
    constraint rrcname1
        unique (rr),
    constraint fk_rr_1
        foreign key (rr) references rr (id)
);

create index RRCNAME2
    on rrcname (cname);

create table rrds
(
    algorithm: int = None
    digest: str = None
    digest_type int                                                                                                                                                                                                   not null,
    id: int = None
        
    key_tag: int = None
    rr: int = None
    ttl: str = None
    constraint rrds1
        unique (rr, key_tag, algorithm, digest_type),
    constraint fk_rr_2
        foreign key (rr) references rr (id)
);

create index RRDS2
    on rrds (key_tag);

create table rrhinfo
(
    cpu: str = None
    id: int = None
        
    os: str = None
    rr: int = None
    ttl: str = None
    constraint fk_rr_3
        foreign key (rr) references rr (id)
);

create index RRHINFO1
    on rrhinfo (rr);

create table rrloc
(
    altitude: int = None
    horiz_pre: str = None
    id: int = None
        
    latitude: str = None
    longitude: str = None
    rr: int = None
    size: str = None
    ttl: str = None
    vert_pre: str = None
    constraint rrloc1
        unique (rr),
    constraint fk_rr_4
        foreign key (rr) references rr (id)
);

create table rrmx
(
    exchange: str = None
    id: int = None
        
    preference int default 0 not null,
    rr: int = None
    ttl: str = None
    constraint rrmx1
        unique (rr, exchange),
    constraint fk_rr_5
        foreign key (rr) references rr (id)
);

create index RRMX2
    on rrmx (exchange);

create table rrnaptr
(
    flags: str = None
    id: int = None
        
    order_field int default 0 not null,
    preference: int = None
    regexpr: str = None
    replacement: str = None
    rr: int = None
    services: str = None
    ttl: str = None
    constraint fk_rr_6
        foreign key (rr) references rr (id)
);

create index RRNAPTR2
    on rrnaptr (rr);

create index RRNAPTR3
    on rrnaptr (services);

create table rrns
(
    id: int = None
        
    nsdname: str = None
    rr: int = None
    ttl: str = None
    constraint rrns1
        unique (rr, nsdname),
    constraint fk_rr_7
        foreign key (rr) references rr (id)
);

create index RRNS2
    on rrns (nsdname);

create table rrptr
(
    id: int = None
        
    ipblock: int = None
    rr: int = None
    ttl: str = None
    ptrdname: str = None
    constraint rrptr1
        unique (ptrdname, ipblock),
    constraint fk_ipblock_3
        foreign key (ipblock) references ipblock (id),
    constraint fk_rr_8
        foreign key (rr) references rr (id)
);

create index RRPTR2
    on rrptr (ipblock);

create index RRPTR3
    on rrptr (rr);

create table rrsrv
(
    id: int = None
        
    port: int = None
    priority int default 0 not null,
    rr: int = None
    target: str = None
    ttl: str = None
    weight: int = None
    constraint rrsrv1
        unique (rr, port, target),
    constraint fk_rr_9
        foreign key (rr) references rr (id)
);

create index RRSRV2
    on rrsrv (target);

create table rrtxt
(
    id: int = None
        
    rr: int = None
    ttl: str = None
    txtdata: str = None
    constraint fk_rr_10
        foreign key (rr) references rr (id)
);

create index RRTXT1
    on rrtxt (rr);

create index RRTXT2
    on rrtxt (txtdata);

create table sitesubnet
(
    id: int = None
        
    site: int = None
    subnet: int = None
    constraint sitesubnet1
        unique (subnet, site),
    constraint fk_site_4
        foreign key (site) references site (id),
    constraint fk_subnet
        foreign key (subnet) references ipblock (id)
);

create table stpinstance
(
    bridge_priority int         null,
    device: int = None
    id: int = None
        
    number: int = None
    root_bridge: str = None
    root_port: int = None
    constraint stpinstance1
        unique (device, number),
    constraint fk_device_7
        foreign key (device) references device (id)
);

create table interfacevlan
(
    id: int = None
        
: int = None
    stp_des_bridge: str = None
    stp_des_port: str = None
    stp_instance: int = None
    stp_state: str = None
    vlan: int = None
    constraint interfacevlan1
        unique (interface, vlan),
    constraint fk_interface_2
        foreign key (interface) references interface (id),
    constraint fk_stp_instance
        foreign key (stp_instance) references stpinstance (id),
    constraint fk_vlan
        foreign key (vlan) references vlan (id)
);

create index InterfaceVlan2
    on interfacevlan (stp_instance);

create index InterfaceVlan3
    on interfacevlan (stp_des_bridge);

create index InterfaceVlan4
    on interfacevlan (stp_des_port);

create index interfacevlan5
    on interfacevlan (vlan);

create index STPInstance2
    on stpinstance (root_bridge);

create table subnetzone
(
    id: int = None
        
    subnet: int = None
    zone: int = None
    constraint subnetzone1
        unique (subnet, zone),
    constraint fk_subnet_1
        foreign key (subnet) references ipblock (id),
    constraint fk_zone_1
        foreign key (zone) references zone (id)
);

create index contactlist
    on zone (contactlist);

create table zonealias
(
    id: int = None
        
    info: str = None
    name: str = None
    zone: int = None
    constraint zonealias1
        unique (name),
    constraint fk_zone_2
        foreign key (zone) references zone (id)
);

create index zone
    on zonealias (zone);


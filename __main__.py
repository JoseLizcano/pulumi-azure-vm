import base64
from pulumi import Config, Output, export, ResourceOptions
from pulumi_azure_native import compute, network, resources

config = Config()
username = config.require("username")
password = config.require("password")

resource_group = resources.ResourceGroup("test-rg")

net = network.VirtualNetwork(
    "test-net",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    subnets=[network.SubnetArgs(
        name="default",
        address_prefix="10.0.1.0/24",
    )]
)

network_security_group = network.NetworkSecurityGroup(
    "test-nsg",
    resource_group_name=resource_group.name,
    location=resource_group.location,
)

#network_security_rule = network.NetworkSecurityRule(
#    "nsgRule",
#    resource_group_name=resource_group.name,
#    network_security_group_name=network_security_group.name,
#    access="Allow",
#    direction="Inbound",
#    protocol="Tcp",
#    source_port_range="*",
#    destination_port_range="22",  # SSH port
#    priority=100,
#    source_address_prefix="*",  # Should be restricted based on your use case
#    destination_address_prefix="*",
#)

public_ip = network.PublicIPAddress(
    "test-ip",
    resource_group_name=resource_group.name,
    public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC)

network_iface = network.NetworkInterface(
    "test-nic",
    resource_group_name=resource_group.name,
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="webserveripcfg",
        subnet=network.SubnetArgs(id=net.subnets[0].id),
        private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
    )])

init_script = """#!/bin/bash

sudo apt-get update -y

echo "Hello, World!" > index.html
nohup python -m SimpleHTTPServer 80 &"""

#cloud_init_data = """#cloud-config
#packages:
#  - slapd
#  - ldap-utils
#runcmd:
#  - DEBIAN_FRONTEND=noninteractive apt-get install -y slapd ldap-utils
#  # Additional commands to configure slapd can go here
#"""

vm = compute.VirtualMachine(
    "test-vm",
    opts=ResourceOptions(replace_on_changes=["*"]),
    resource_group_name=resource_group.name,
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[
            compute.NetworkInterfaceReferenceArgs(id=network_iface.id),
        ],
    ),
    hardware_profile=compute.HardwareProfileArgs(
        vm_size=compute.VirtualMachineSizeTypes.STANDARD_B1S,
    ),
    os_profile=compute.OSProfileArgs(
        computer_name="hostname",
        admin_username=username,
        admin_password=password,
        #custom_data=cloud_init_data,
        custom_data=base64.b64encode(init_script.encode("ascii")).decode("ascii"),
        linux_configuration=compute.LinuxConfigurationArgs(
            disable_password_authentication=False,
        ),
    ),
    storage_profile=compute.StorageProfileArgs(
        os_disk=compute.OSDiskArgs(
            create_option=compute.DiskCreateOptionTypes.FROM_IMAGE,
            name="myosdisk1",
        ),
        image_reference=compute.ImageReferenceArgs(
            publisher="canonical",
            offer="UbuntuServer",
            sku="16.04-LTS",
            version="latest",
        ),
    ))

public_ip_addr = vm.id.apply(lambda _: network.get_public_ip_address_output(
    public_ip_address_name=public_ip.name,
    resource_group_name=resource_group.name))

export("public_ip", public_ip_addr.ip_address)
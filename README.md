# Azure Virtual Machine

This example deploys an Azure Virtual Machine.

## Prerequisites

1. [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
2. [Configure Pulumi for Azure](https://www.pulumi.com/docs/intro/cloud-providers/azure/setup/)
3. [Configure Pulumi for Python](https://www.pulumi.com/docs/intro/languages/python/)

## Deploying and running the program

1. Create a new stack:

    ```bash
    $ pulumi stack init dev
    ```

2. Set the required configuration for this example. This example requires you to supply a username and password to the virtual machine that we are going to create.

    ```
    $ pulumi config set azure-native:location westus    # any valid Azure region will do
    $ pulumi config set username webmaster
    $ pulumi config set password --secret <your-password>

    Note that `--secret` ensures your password is encrypted safely.

    $ az login
    $ az account list
    $ az account set --subscription=<id>

3. Run `pulumi up` to preview and deploy the changes:

    ```
    $ pulumi update
    Previewing update (dev):

     Type                                          Name                   
 +   pulumi:pulumi:Stack                           pulumi-azure-vm-dev
 +   ├─ azure-native:resources:ResourceGroup       test-rg                
 +   ├─ azure-native:network:VirtualNetwork        test-net               
 +   ├─ azure-native:network:PublicIPAddress       test-ip                
 +   ├─ azure-native:network:NetworkInterface      test-nic
 +   └─ azure-native:compute:VirtualMachine        test-vm
Outputs:
    public_ip: output<string>

Resources:
    + 7 to create

    Do you want to perform this update? yes
    Updating (dev):

     Type
 +   pulumi:pulumi:Stack
 +   ├─ azure-native:resources:ResourceGroup
 +   ├─ azure-native:network:VirtualNetwork
 +   ├─ azure-native:network:PublicIPAddress
 +   ├─ azure-native:network:NetworkInterface
 +   └─ azure-native:compute:VirtualMachine
Outputs:
    public_ip: "20.253.173.106"

Resources:
    + 7 created

Duration: 43s

    ```

4. Get the IP address of the newly-created instance from the stack's outputs: 

    ```bash
    $ pulumi stack output public_ip
    20.253.173.10
    ```

5. Check to see that your server is now running:

    ```
    $ curl http://$(pulumi stack output public_ip)
    Hello, World!
    ```

1. Destroy the stack:

    ```bash
    ▶ pulumi destroy --yes
    ```
